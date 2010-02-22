##
# tcp_client_load.py
##

import socket
import time
import threading
import sys
import os

def create_tcp_client(aim = 'default'):
	tcpclient = TCPClient('localhost', 9999)
	#tcpclient.handle()
	#tcpclient.write('<policy-file-request/>')
	#tcpclient.write('{"cmd":"getStatus", "args": "null", "channel": "null", "app" : "null"}\n')
	#tcpclient.handle()
	
	tcpclient.write('{"cmd":"setStatus", "app" : "null"}\n')
	#tcpclient.handle()
	tcpclient.write('{"cmd":"setStatus", "args" : "hello"}\n')
	tcpclient.handle()
	tcpclient.write('{"cmd":"getStatus", "args":"null", "channel": "null", "app" : "null"}\n')
	tcpclient.handle()
	tcpclient.write('{"cmd":"message", "args":"[\'HELLO\', [\'*ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd\']]", "channel": "irc", "app" : "whiteboard"}\n')
	tcpclient.handle()
	tcpclient.write('{"cmd":"forward", "args":"[\'HELLO\', [\'*\']]", "channel": "irc", "app" : "whiteboard"}\n')
	tcpclient.handle()
	tcpclient.write('{"cmd":"join", "args": ["CHANNELQUIEXISTEPAS"], "channel": "null", "app" : "whiteboard"}\n')
	tcpclient.handle()
	tcpclient.write('{"cmd":"part", "args": "CHANNELQUIEXISTEPAS", "channel": "null", "app" : "whiteboard"}\n')
	tcpclient.handle()
	tcpclient.write('{"cmd":"join", "args": ["irc"], "channel": "irc", "app" : "whiteboard"}\n')
	tcpclient.handle()
	tcpclient.write('{"cmd":"chanAuth", "args": "admin", "channel": "irc", "app" : "whiteboard"}\n')
	tcpclient.handle()
	tcpclient.write('{"cmd":"timeConnect", "args": "null", "channel": "null", "app" : "whiteboard"}\n')
	tcpclient.handle()
	tcpclient.write('{"cmd":"create", "args": ["toto", "tata"], "channel": "null", "app" : "whiteboard"}\n')
	tcpclient.handle()
	tcpclient.write('{"cmd":"join", "args": ["toto", "tata"], "channel": "null", "app" : "whiteboard"}\n')
	tcpclient.handle()
	tcpclient.write('{"cmd":"chanMasterPwd", "args": "joejoe", "channel": "toto", "app" : "whiteboard"}\n')
	tcpclient.handle()
	tcpclient.write('{"cmd":"chanAuth", "args": "joejoe", "channel": "toto", "app" : "whiteboard"}\n')
	tcpclient.handle()
	time.sleep(5)
	tcpclient.disconnect()
	
def create_tcp_client_(aim = 'default'):
	tcpclient = TCPClient('localhost', 9999)
	#tcpclient.handle()
	tcpclient.write('{"cmd":"join", "args":"irc", "app": "irc"}\n')
	tcpclient.handle()
	tcpclient.write('{"cmd":"message", "args":[ "Coucou !", [ "master" ] ], "app": "irc"}\n')
	tcpclient.handle()
	time.sleep(5)
	tcpclient.disconnect()
 
def main():
	client_thread = threading.Thread(target=create_tcp_client, args=())
	client_thread.start()
	for i in range(0,2):
		client_thread = threading.Thread(target=create_tcp_client_, args=())
		client_thread.start()
	print '[i] Press ^C to exit'
	while True:
		try:
			toto = sys.stdin.readline()
		except KeyboardInterrupt:
			os._exit(1)

class TCPClient(object):
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.sock = None
		self.buffer = ''
		self.connect()

	def connect(self):
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error, msg:
			sys.stderr.write("[!] %s\n" % msg[1])
			sys.exit(1)
		try:
			self.sock.connect((self.host, self.port))
		except socket.error, msg:
			sys.stderr.write("[!] %s\n" % msg[1])
			sys.exit(2)

	def handle(self):
		self.buffer = self.sock.recv(1024)
		print self.buffer

	def write(self, str):
		self.sock.send(str)

	def disconnect(self):
		self.sock.close()

if __name__ == '__main__':
	main()