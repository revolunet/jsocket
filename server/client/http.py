##
# http.py
##

import threading
from commons.protocol import Protocol
from log.logger import Log
from config.settings import SETTINGS
from request import Request
from response import Response
import simplejson
import urllib

class ClientHTTP(threading.Thread):
	def __init__(self, client_socket, client_address, room, rqueue, squeue):
		self.protocol = Protocol(self)
		self.client_socket = client_socket
		self.client_address = client_address
		self.rqueue = rqueue
		self.squeue = squeue
		self.request = Request()
		self.response = Response()
		threading.Thread.__init__(self)
		
	def run(self):
		"""lecture du client """
		
		try:
			data = buffer = self.client_socket.recv(SETTINGS.SERVER_MAX_READ).strip()
			while len(buffer) == SETTINGS.SERVER_MAX_READ:
				buffer = self.client_socket.recv(SETTINGS.SERVER_MAX_READ).strip()
				data = data + buffer
			self.request.handle(data)
			#self.handleMethod()
			
			self.response.ResponseData("aaaaaaaaaaaaaaaaaaaaaaaaaa aaaaaaaaaaaaaaaaaaaaaaaaa<u>iiii</u>")
			self.client_socket.send(self.response.Get(self.request, 200))
			self.__disconnection()
			
		except Exception as e:
			self.__disconnection()
			return
			
	def handleMethod(self):
		if self.request.method == 'options':
			pass
		else:
			if self.request.post_Ket_Exists("json") and len(self.request.post_DATA("json")) > 0:
				self.rqueue.put([self, urllib.unquote_plus(self.request.post_DATA("json"))])
				print urllib.unquote_plus(self.request.post_DATA("json"))
				
	def __disconnection(self):
		"""On ferme la socket serveur du client lorsque celui-ci a ferme sa socket cliente"""
		
		self.client_socket.close()
		Log().add("[-] HTTP Client disconnected", 'blue')