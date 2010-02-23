##
# client.py
##

import threading
from commons.protocol import Protocol
from log.logger import Log
from config.settings import SETTINGS

class ClientTCP(threading.Thread):
	def __init__(self, client_socket, client_address, room, rqueue, squeue):
		import time
		import random
		
		self.protocol = Protocol(self)
		
		self.client_socket = client_socket
		self.client_address = client_address
		self.master = False
		self.nickName = None
		self.room = room
		self.master_password = SETTINGS.MASTER_PASSWORD
		self.unique_key = hex(random.getrandbits(64))
		self.rqueue = rqueue
		self.squeue = squeue
		self.room_name = None
		self.status = "online"
		self.connection_time = time.strftime('%x %X')
		threading.Thread.__init__(self)

	def run(self):
		"""Boucle de lecture du client """

		while 1:
			try:
				data = buffer = self.client_socket.recv(SETTINGS.SERVER_MAX_READ).strip()
				while len(buffer) == SETTINGS.SERVER_MAX_READ:
					buffer = self.client_socket.recv(SETTINGS.SERVER_MAX_READ).strip()
					data = data + buffer
			except Exception:
				self.__disconnection()
				return
			if len(data) == 0:
				self.__disconnection()
				return
			else:
				self.rqueue.put([self, data])
				Log().add("[+] Client " + str(self.client_address) + " send : " + data)

	def get_name(self):
		if self.nickName == None:
			return self.unique_key
		return self.nickName

	def queue_cmd(self, command):
		"""Ajoute une commande a la Queue en cours"""
		
		self.squeue.put([self.protocol, command])
				
	def __master_logout(self):
		
		rooms = self.room.rooms
		for channel in rooms:
			if rooms[channel].master == self:
				for user in rooms[channel].client_list:
					if user.master == False:
						Log().add("[+] Envoie du status master au client : " + user.get_name(), 'blue')
						self.squeue.put([user.protocol, '{"from": "status", "value": ["master", "offline"]}'])
		
	def __disconnection(self):
		"""On ferme la socket serveur du client lorsque celui-ci a ferme sa socket cliente"""

		if self.master == True:
			self.__master_logout()
		
		rooms = self.room.rooms
		for channel in rooms:
			for user in rooms[channel].client_list:
				if user == self:
					self.room.part(channel, self)
					
		self.status = "offline"
		self.protocol.status(self)
		self.client_socket.close()
		Log().add("[-] Client disconnected", 'blue')
