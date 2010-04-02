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
from server.watchdog import WatchDog
from commons.jexception import JException
import simplejson
import urllib

class ClientHTTP(IClient):
	def __init__(self, client_socket, client_address, room, rqueue, squeue, http_list):
		#self.protocol = Protocol(self)
		self.client_socket = client_socket
		self.client_address = client_address
		#self.rqueue = rqueue
		#self.squeue = squeue
		self.request = Request()
		self.response = Response()
		self.validJson = False
		IClient.__init__(self, room, rqueue, squeue, 'http', http_list)
		#threading.Thread.__init__(self)
		
	def get_name(self):
		if self.nickName == None:
			return self.unique_key
		return self.nickName

	def run(self):
		"""lecture du client """
		try:
			data = buffer = self.client_socket.recv(SETTINGS.SERVER_MAX_READ).strip()
			while len(buffer) == SETTINGS.SERVER_MAX_READ:
				buffer = self.client_socket.recv(SETTINGS.SERVER_MAX_READ).strip()
				data = data + buffer
			self.request.handle(data)
			
			if self.request.post_DATA('json') is not None:
				if len(self.request.post_DATA('json')) != 0:
					try:
						json_data = urllib.unquote_plus(self.request.post_DATA('json')).split('\n')
						for data in json_data:
							data = data.strip()
							if len(data) > 0:
								json_cmd = simplejson.loads(data)
								if json_cmd['cmd'] == 'connected':
									self.validJson = True
									self.client_socket.send('{"from": "connected", "value": "'+self.unique_key+'", "app": ""}')
									self.disconnection()
								elif json_cmd['cmd'] == 'refresh':
									for s in self.http_list.get(json_cmd.get('uid')):
										if len(s) > 0:
											self.client_socket.send(s + '\n')
									self.http_list[json_cmd['uid']] = [ ]
									self.disconnection()
								else:
									self.validJson = True
									self.rput(data)
					except Exception:
						Log().add(JException().formatExceptionInfo())
			#self.client_socket.send(self.response.Get(self.request, 200))
			
		except Exception as e:
			Log().add(JException().formatExceptionInfo())
			self.disconnection()
			return
	
	# outdated
	def handleMethod(self):
		if self.request.method == 'options':
			pass
		else:
			if self.request.post_Ket_Exists("json") and len(self.request.post_DATA("json")) > 0:
				self.rqueue.put([self, urllib.unquote_plus(self.request.post_DATA("json"))])
	
	def queue_cmd(self, command):
		"""Ajoute une commande a la Queue en cours"""
		
		self.sput(command)
	
	def disconnection(self):
		"""On ferme la socket serveur du client lorsque celui-ci a ferme sa socket cliente"""
		
		if self.client_socket is not None:
			self.client_socket.close()
			self.client_socket = None
			Log().add("[-] HTTP Client disconnected", 'blue')