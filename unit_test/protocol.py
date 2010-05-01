import simplejson
import socket
import time
import threading
import sys
import os
import urllib
import urllib2

class CONFIG(object):
	IS_DEBUG = False
	SERVER_PORT = 9999
	#SERVER_PORT = 8080
	CLIENT_NUMBER = 100
	CLIENT_THREAD = True
	#SERVER_HOST = socket.gethostbyname(socket.gethostname())
	SERVER_HOST = 'localhost'
	HTTP_SERVER_PORT = 81
	SERVER_SELECT_TIMEOUT = 5
	SERVER_MAX_READ = 1024
	SERVER_HTTP_CLIENT_TIMEOUT = 30 # !important

class Stats(object):
	instance = None

	def __new__(this):
		if this.instance is None:
			this.instance = object.__new__(this)
			this.errorTotal = 0
			this.errors = { }
			this.errorsDetails = { }
			this.begin = time.time()
		return this.instance

	def start(self):
		pass

	def add(self, command, detail):
		if self.errors.get(command, None) is None:
			self.errors[command] = 0
			self.errorsDetails[command] = [ ]
		self.errors[command] += 1
		self.errorTotal += 1
		self.errorsDetails[command].append("\n" + detail)

	def show(self):
		print '-----------------------------------------------------------------------'
		print 'Server:'
		print ' - Host: %s' % str(CONFIG.SERVER_HOST)
		print ' - TCP port: %d' % CONFIG.SERVER_PORT
		print ' - HTTP port: %d' % CONFIG.HTTP_SERVER_PORT
		print '-----------------------------------------------------------------------'
		print 'Results:'
		print '-----------------------------------------------------------------------'
		totalTime = float(time.time() - self.begin)
		totalCommand = len(Protocol.commands) * CONFIG.CLIENT_NUMBER
		print ' - Total executed commands: %d (%d commands per clients)' % (totalCommand, len(Protocol.commands))
		print ' - Total time (secs): %s (avg. %s per commands / avg. %s per clients)' % (str(totalTime), str(totalTime / totalCommand), str(totalTime / CONFIG.CLIENT_NUMBER))
		print ' - For %d Clients it founds %d errors (%s %% chance per command)' % (CONFIG.CLIENT_NUMBER, self.errorTotal, str(float(self.errorTotal) / float(totalCommand)))
		print '-----------------------------------------------------------------------'
		if self.errorTotal == 0:
			print ' - No error found. You make a great JusDeChaussette TODAY !'
			print '-----------------------------------------------------------------------'
			return True
		print 'Errors:'
		for (command, nbError) in self.errors.items():
			print '[%s] Found %d errors' % (command, nbError)
			if CONFIG.IS_DEBUG == True:
				print '[%s] Details:' % command
				for detail in self.errorsDetails[command]:
					print detail
		print '-----------------------------------------------------------------------'
		return False

class HTTPClient(object):
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.buffer = ''
		self.uid = ''

	def write(self, json):
		params = urllib.urlencode({'json': json})
		req = urllib2.Request('http://' + CONFIG.SERVER_HOST + ':' + str(CONFIG.HTTP_SERVER_PORT) + '/', params)
		response = urllib2.urlopen(req)
		self.buffer = response.read()

	def handle(self):
		if len(self.buffer) > 0:
			res = self.buffer
			self.buffer = ''
			return res
		params = urllib.urlencode({'json': Protocol.commands.get('refresh', '').replace('$uid', self.uid)})
		req = urllib2.Request('http://' + CONFIG.SERVER_HOST + ':' + str(CONFIG.HTTP_SERVER_PORT) + '/', params)
		response = urllib2.urlopen(req)
		self.buffer = response.read()
		return self.buffer

	def disconnect(self):
		pass

class TCPClient(object):
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.sock = None
		self.uid = ''
		self.buffer = ''
		self.connect()

	def connect(self):
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		except socket.error, msg:
			sys.stderr.write("[!] %s\n" % msg[1])
			sys.exit(1)
		try:
			self.sock.connect((self.host, self.port))
		except socket.error, msg:
			sys.stderr.write("[!] %s\n" % msg[1])
			sys.exit(2)

	def handle(self):
		self.buffer = self.sock.recv(4096)
		return self.buffer

	def write(self, json):
		self.sock.send(json)

	def disconnect(self):
		self.sock.close()

class Protocol(object):
	commands = {
		'refresh': '{"cmd": "refresh", "args": "null", "uid": "$uid", "channel": "protocol", "app": "protocol"}',
		'connected': '{"cmd": "connected", "args": "null"}',
		'auth': '{"cmd": "auth", "args": "admin", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'create': '{"cmd": "create", "args": [ "protocol", "password" ], "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'join': '{"cmd": "join", "args": [ "protocol", "password" ], "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'chanMasterPwd': '{"cmd": "chanMasterPwd", "args": "passwordChan", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'chanAuth': '{"cmd": "chanAuth", "args": "passwordChan", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'nick': '{"cmd": "nick", "args": "protocolMaster", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'forward': '{"cmd": "forward", "args": "messageToForward", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'list': '{"cmd": "list", "args": "protocol", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'message': '{"cmd": "message", "args": ["message", [ "unknown" ]], "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'setStatus': '{"cmd": "setStatus", "args": "protocolMasterNewStatus", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'getStatus': '{"cmd": "getStatus", "args": "null", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'timeConnect': '{"cmd": "timeConnect", "args": "null", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'part': '{"cmd": "part", "args": "protocol", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'remove': '{"cmd": "remove", "args": "protocol", "app": "protocol", "channel": "protocol", "uid": "$uid"}'
	}
	neededKeys = [
		'from',
		'value',
	]
	defaultKeys = [
		'app',
		'channel'
	]
	errorKeys = [
		'message'
	]

	@staticmethod
	def connected(client):
		method = 'connected'
		client.write(Protocol.commands.get(method, ''))
		result = client.handle().strip(' \t\n\0')
		json = Protocol.checkJson(method, result)
		if json == False:
			return False
		if Protocol.checkKeys(method, json, Protocol.neededKeys) == False:
			return False
		client.uid = json.get('value', '')
		return True

	@staticmethod
	def stdCommand(method, client):
		client.write(Protocol.commands.get(method, '').replace('$uid', client.uid))
		results = client.handle().strip(' \t\n\0').split("\n")
		for result in results:
			json = Protocol.checkJson(method, result)
			if json == False:
				return False
			if Protocol.checkKeys(method, json, Protocol.neededKeys + Protocol.defaultKeys) == False:
				return False
		return True

	@staticmethod
	def checkJson(name, jsonEncoded):
		try:
			jsonDecoded = simplejson.loads(jsonEncoded)
			return jsonDecoded
		except ValueError:
			error = '[%s] JSON malformed' % name
			error += '[%s][DEBUG] %s' % (name, jsonEncoded)
			Stats().add(name, error)
			return False

	@staticmethod
	def checkKeys(name, json, keys):
		result = True
		for k in keys:
			if json['from'] == 'status' and k == 'app':
				continue
			if json.get(k, None) is None:
				result = False
				error = '[%s] JSON key "%s" missing' % (name, k)
				error += '[%s][DEBUG] %s' % (name, str(json))
				Stats().add(name, error)
		return result

def protocolTesting(*args):
	index = args[0]
	client = HTTPClient(CONFIG.SERVER_HOST, CONFIG.HTTP_SERVER_PORT)
	#client = TCPClient(CONFIG.SERVER_HOST, CONFIG.SERVER_PORT)
	Protocol.connected(client)
	Protocol.stdCommand('auth', client)
	Protocol.stdCommand('create', client)
	Protocol.stdCommand('join', client)
	Protocol.stdCommand('chanMasterPwd', client)
	Protocol.stdCommand('chanAuth', client)
	Protocol.stdCommand('nick', client)
	Protocol.stdCommand('forward', client)
	Protocol.stdCommand('list', client)
	Protocol.stdCommand('message', client)
	Protocol.stdCommand('setStatus', client)
	Protocol.stdCommand('getStatus', client)
	Protocol.stdCommand('timeConnect', client)
	Protocol.stdCommand('part', client)
	Protocol.stdCommand('remove', client)
	client.disconnect()
	print '[i] Client n%d finished' % index

def main():
	Stats().start()
	threads = [ ]
	for i in range(0, CONFIG.CLIENT_NUMBER):
		print '[i] Launching client n%d' % i
		if CONFIG.CLIENT_THREAD == True:
			threadHTTP = threading.Thread(target=protocolTesting, args=([ i ]))
			threadHTTP.start()
			threads.append(threadHTTP)
		else:
			protocolTesting(i)
	if len(threads) > 0:
		for t in threads:
			t.join()
	Stats().show()
	print '[i] Press ^C to exit'
	while True:
		try:
			toto = sys.stdin.readline()
		except KeyboardInterrupt:
			os._exit(1)

if __name__ == '__main__':
	main()
