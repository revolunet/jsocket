##
# server.py
##

import socket
import sys
import select
import Queue
from client.tcp import ClientTCP
from commons.room import Room
from log.logger import Log
from commons.worker import Worker
from config.settings import SETTINGS
import threading

class ServerTCP(threading.Thread):
	"""docstring for Server"""
	def __init__(self, room, squeue, rqueue):
		self.__host = SETTINGS.SERVER_HOST
		self.__port = SETTINGS.SERVER_PORT
		self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.__socket.bind((self.__host, self.__port))
		self.__socket.listen(5)
		Log().add("[+] TCP Server launched on %s:%d" % (self.__host, self.__port), "green")
		self.__room = room
		self.__init_queues(squeue, rqueue)
		#windows define
		import os
		if os.name != 'nt':
			self.__input = [self.__socket, sys.stdin]
		else:
			self.__input = [self.__socket]
		threading.Thread.__init__(self)

	def __init_queues(self, squeue, rqueue):
		""" Initialise les queues d'envoie et reception (parsing) de message client """

		self.__squeue = squeue
		self.__rqueue = rqueue
		#self.__squeue = Queue.Queue(0)
		#Worker(self.__squeue, 'send').start()
		#self.__rqueue = Queue.Queue(0)
		#Worker(self.__rqueue, 'recv').start()

	def run(self):
		while 1:
			try:
				inputready,outputready,exceptready = select.select(self.__input,[],[], SETTINGS.SERVER_SELECT_TIMEOUT) 
				for s in inputready:
					if s == self.__socket: 
						# handle the server socket 
						client_socket, client_addr = self.__socket.accept()
						Log().add("[+] TCP Client connected " + (str(client_addr)))
						current_client = ClientTCP(client_socket, client_addr, self.__room, self.__rqueue, self.__squeue)
						current_client.start()
					elif s == sys.stdin: 
						# handle standard input 
						junk = sys.stdin.readline() 
						running = 0
					else: 
						# handle all other sockets 
						data = s.recv(size) 
						if data: 
							s.send(data) 
						else: 
							s.close() 
							input.remove(s)
			except KeyboardInterrupt:
				self.__socket.close()
				Log().add("[-] TCP Server Killed", 'ired')
				exit()
				return