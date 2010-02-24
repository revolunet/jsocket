##
# http.py
##

import threading
from commons.protocol import Protocol
from log.logger import Log
from config.settings import SETTINGS
from request import Request

class ClientHTTP(threading.Thread):
	def __init__(self, client_socket, client_address, room, rqueue, squeue):
		self.client_socket = client_socket
		self.client_address = client_address
		self.rqueue = rqueue
		self.squeue = squeue
		self.request = Request()
		threading.Thread.__init__(self)
		
	def run(self):
		data = buffer = self.client_socket.recv(SETTINGS.SERVER_MAX_READ).strip()
		while len(buffer) == SETTINGS.SERVER_MAX_READ:
			buffer = self.client_socket.recv(SETTINGS.SERVER_MAX_READ).strip()
			data = data + buffer
		self.request.handle(data)