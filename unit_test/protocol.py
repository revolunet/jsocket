import simplejson
import socket
import time
import threading
import sys
import os
import urllib
import urllib2

class CONFIG(object):
	IS_DEBUG = True
	SERVER_PORT = 9999
	#SERVER_PORT = 8080
	CLIENT_NUMBER = 100
	CLIENT_THREAD = False
	#SERVER_HOST = socket.gethostbyname(socket.gethostname())
	SERVER_HOST = 'localhost'
	HTTP_SERVER_PORT = 81
	SERVER_SELECT_TIMEOUT = 5
	SERVER_MAX_READ = 1024
	SERVER_HTTP_CLIENT_TIMEOUT = 30 # !important

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
		if CONFIG.IS_DEBUG == True:
			print 'Sent: \'%s\'' % json
			print self.buffer

	def handle(self):
		if len(self.buffer) > 0:
			res = self.buffer
			self.buffer = ''
			return res
		params = urllib.urlencode({'json': Protocol.commands.get('refresh', '').replace('$uid', self.uid)})
		req = urllib2.Request('http://' + CONFIG.SERVER_HOST + ':' + str(CONFIG.HTTP_SERVER_PORT) + '/', params)
		response = urllib2.urlopen(req)
		self.buffer = response.read()
		if CONFIG.IS_DEBUG == True:
			print self.buffer
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
		if CONFIG.IS_DEBUG == True:
			print 'Sent: \'%s\'' % json
		self.sock.send(json)

	def disconnect(self):
		self.sock.close()

class Protocol(object):
	commands = {
		'refresh': '{"cmd": "refresh", "args": "null", "uid": "$uid", "channel": "protocol", "app": "protocol"}',
		'connected': '{"cmd": "connected", "args": "null"}',
		'auth': '{"cmd": "auth", "args": "admin", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'create': '{"cmd": "create", "args": [ "protocol", "password" ], "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'join': '{"cmd": "join", "args": "protocol", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'chanMasterPwd': '{"cmd": "chanMasterPwd", "args": "passwordChan", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'chanAuth': '{"cmd": "chanAuth", "args": "passwordChan", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'nick': '{"cmd": "nick", "args": "protocolMaster", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'forward': '{"cmd": "forward", "args": "messageToForward", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'list': '{"cmd": "list", "args": "protocol", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'message': '{"cmd": "message", "args": ["message", [ "*" ]], "app": "protocol", "channel": "protocol", "uid": "$uid"}',
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
		if CONFIG.IS_DEBUG == True:
			print '[%s] Result correct' % method
			print '[%s] %s' % (method, result)
		return True

	@staticmethod
	def stdCommand(method, client):
		client.write(Protocol.commands.get(method, '').replace('$uid', client.uid))
		result = client.handle().strip(' \t\n\0')
		json = Protocol.checkJson(method, result)
		if json == False:
			return False
		if Protocol.checkKeys(method, json,
			Protocol.neededKeys + Protocol.defaultKeys) == False:
			return False
		if CONFIG.IS_DEBUG == True:
			print '\n[%s] Result correct' % method
			print '[%s] %s' % (method, result)
		return True

	@staticmethod
	def checkJson(name, jsonEncoded):
		try:
			jsonDecoded = simplejson.loads(jsonEncoded)
			return jsonDecoded
		except ValueError:
			if CONFIG.IS_DEBUG == True:
				print '[%s] JSON malformed' % name
				print '[%s][DEBUG] %s' % (name, jsonEncoded)
			return False

	@staticmethod
	def checkKeys(name, json, keys):
		result = True
		for k in keys:
			if json.get(k, None) is None:
				result = False
				if CONFIG.IS_DEBUG == True:
					print '[%s] JSON key "%s" missing' % (name, k)
					print '[%s][DEBUG] %s' % (name, str(json))
		return result

def protocolTesting():
	client = HTTPClient(CONFIG.SERVER_HOST, CONFIG.HTTP_SERVER_PORT)
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

def main():
	import time

	t = time.time()
	for i in range(0, CONFIG.CLIENT_NUMBER):
		if CONFIG.CLIENT_THREAD == True:
			#threadTCP = threading.Thread(target=protocolTesting, args=TCPClient(CONFIG.SERVER_HOST, CONFIG.SERVER_PORT))
			#threadTCP.start()
			threadHTTP = threading.Thread(target=protocolTesting, args=())
			threadHTTP.start()
		else:
			#protocolTesting(TCPClient(CONFIG.SERVER_HOST, CONFIG.SERVER_PORT))
			protocolTesting()
	print str(time.time() - t) + ' secs'
	print '[i] Press ^C to exit'
	while True:
		try:
			toto = sys.stdin.readline()
		except KeyboardInterrupt:
			os._exit(1)

if __name__ == '__main__':
	main()
