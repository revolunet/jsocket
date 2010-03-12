##
# http.py
##

#import threading
#from commons.protocol import Protocol
from client.iClient import IClient
from log.logger import Log
from config.settings import SETTINGS
from request import Request
from response import Response
import simplejson
import urllib

class ClientHTTP(IClient):
	def __init__(self, client_socket, client_address, room, rqueue, squeue):
		#self.protocol = Protocol(self)
		self.client_socket = client_socket
		self.client_address = client_address
		#self.rqueue = rqueue
		#self.squeue = squeue
		self.request = Request()
		self.response = Response()
		IClient.__init__(self, room, rqueue, squeue, 'http')
		#threading.Thread.__init__(self)
		
	def run(self):
		"""lecture du client """
		
		try:
			data = buffer = self.client_socket.recv(SETTINGS.SERVER_MAX_READ).strip()
			while len(buffer) == SETTINGS.SERVER_MAX_READ:
				buffer = self.client_socket.recv(SETTINGS.SERVER_MAX_READ).strip()
				data = data + buffer
			self.request.handle(data)
			
			if self.request.post_DATA('json') is not None:
				self.rput(urllib.unquote_plus(self.request.post_DATA('json')))
			self.__disconnection()
			#self.client_socket.send(self.response.Get(self.request, 200))
			
		except Exception as e:
			self.__disconnection()
			return
	
	# outdated
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