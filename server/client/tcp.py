##
# client.py
##

import time
import random
import threading
import simplejson
from client.iClient import IClient
from commons.protocol import Protocol
from log.logger import Log
from config.settings import SETTINGS
from commons.jexception import JException

class ClientTCP(IClient):
	def __init__(self, client_socket, client_address, room, rqueue, squeue, http_list):
		self.client_socket = client_socket
		self.client_address = client_address
		IClient.__init__(self, room, rqueue, squeue, 'tcp', http_list)

	def run(self):
		"""Boucle de lecture du client """

		while 1:
			try:
				data = buffer = self.client_socket.recv(SETTINGS.SERVER_MAX_READ).strip()
				while len(buffer) == SETTINGS.SERVER_MAX_READ:
					buffer = self.client_socket.recv(SETTINGS.SERVER_MAX_READ).strip()
					data = data + buffer
			except KeyboardInterrupt:
				raise
			except Exception:
				self.__disconnection()
				return
			if len(data) == 0:
				self.__disconnection()
				return
			else:
				self.rput(data)
				Log().add("[+] Client " + str(self.client_address) + " send : " + data)

	def get_name(self):
		"""Return : Si l utilisateur n a pas de nickname on retourne la unique_key sinon son nickmae -> string """
		
		if self.nickName == None:
			return self.unique_key
		return self.nickName

	def queue_cmd(self, command):
		"""Ajoute une commande a la Queue en cours"""
		
		self.sput(command)
				
	def __master_logout(self):
		"""
		Lorsque le master se deconnecte on l'efface du server.
		"""
		
		rooms = self.room.rooms
		for channel in rooms:
			if rooms[channel].master == self:
				for user in rooms[channel].client_list:
					if user.master == False:
						to_send = {"name": "Master", "key": "null", "status": "offline"}
						Log().add("[+] Envoie du status master au client : " + user.get_name(), 'blue')
						user.sput('{"from": "status", "value": '+ simplejson.JSONEncoder().encode(to_send) +', "channel": "'+user.room_name+'"}')
		
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
		self.client_socket = None
		Log().add("[-] TCP Client disconnected", 'blue')
