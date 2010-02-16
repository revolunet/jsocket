##
# client.py
##

import threading
import json
import random
from protocol import Protocol
from json import JSONEncoder
from log import Log
from settings import *

class Client(threading.Thread):
	def __init__(self, client_socket, client_address, room, rqueue, squeue):
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
		self.status = "connected"
		threading.Thread.__init__(self)

	def run(self):
		"""Boucle de lecture du client """

		while 1:
			data = self.client_socket.recv(1024).strip()
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
		
		self.squeue.put([self, command])
				
	def __disconnection(self):
		"""On ferme la socket serveur du client lorsque celui-ci a ferme sa socket cliente"""

		if self.room_name:
			self.room.part(self.room_name, self)			
		self.client_socket.close()
		Log().add("[-] Client disconnected", 'blue')
