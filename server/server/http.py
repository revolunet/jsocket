# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <nopz> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return Nopz
# ----------------------------------------------------------------------------

import sys
import socket
import select
import threading
from log.logger import Log
from config.settings import SETTINGS
from client.http import ClientHTTP

class ServerHTTP(threading.Thread):
	"""docstring for ServerHTTP"""
	def __init__(self, room, rqueue, squeue):
		self.__host = SETTINGS.SERVER_HOST
		self.__room = room
		self.__rqueue = rqueue
		self.__squeue = squeue
		
		self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.__socket.bind((self.__host, 8001))
		self.__socket.listen(5)
		Log().add("[+] HTTP Server launched on %s:%d" % (self.__host, 80), "green")
		self.__input = [self.__socket]
		threading.Thread.__init__(self)

	def run(self):
		while 1:
			try:
				inputready,outputready,exceptready = select.select(self.__input,[],[], SETTINGS.SERVER_SELECT_TIMEOUT)
				for s in inputready:
					if s == self.__socket:
						client_socket, client_addr = self.__socket.accept()
						client_socket.settimeout(2)
						Log().add("[+] HTTP Client connected " + (str(client_addr)))
						current_client = ClientHTTP(client_socket, client_addr, self.__room, self.__rqueue, self.__squeue)
						current_client.setDaemon(True)
						current_client.start()
			except KeyboardInterrupt:
				self.__socket.close()
				Log().add("[-] HTTP Server Killed", 'ired')
				exit()
				return