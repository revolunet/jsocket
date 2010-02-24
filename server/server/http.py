# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <nopz> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return Nopz
# ----------------------------------------------------------------------------

import sys
import socket
import select
from log.logger import Log
from config.settings import SETTINGS
from client.http import ClientHTTP

class ServerHTTP(object):
	"""docstring for ServerHTTP"""
	def __init__(self, room, rqueue, squeue):
		self.__host = SETTINGS.SERVER_HOST
		self.__room = room
		self.__rqueue = rqueue
		self.__squeue = squeue
		
		self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.__socket.bind((self.__host, 80))
		self.__socket.listen(5)
		self.__input = [self.__socket]

	def start(self):
		while 1:
			try:
				inputready,outputready,exceptready = select.select(self.__input,[],[], SETTINGS.SERVER_SELECT_TIMEOUT)
				for s in inputready:
					if s == self.__socket:
						client_socket, client_addr = self.__socket.accept()
						Log().add("[+] Client connected " + (str(client_addr)))
						current_client = ClientHTTP(client_socket, client_addr, self.__room, self.__rqueue, self.__squeue)
						current_client.start()
			except KeyboardInterrupt:
				self.__socket.close()
				exit()