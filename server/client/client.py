import time
import random
from config.settings import SETTINGS
from log.logger import Log

class Client(object):
	"""
	Interface commune aux clients TCP et HTTP.
	Regroupe les informations qui caracterise un client.
	"""

	def __init__(self, room):
		"""
		HTTP/TCP Client constructeur.
		"""

		self.room = room
		self.master = False
		self.nickName = None
		self.master_password = SETTINGS.MASTER_PASSWORD
		self.unique_key = str(hex(random.getrandbits(64)))
		self.status = 'online'
		self.connection_time = int(time.time())
		self.last_action = self.connection_time
		self.room_name = None
		self.response = [ ]

	def getName(self):
		"""Return : Si l utilisateur n a pas de nickname on retourne la unique_key sinon son nickname -> string """

		if self.nickName == None:
			return self.unique_key
		return self.nickName

	def addResponse(self, command):
		"""Ajoute une commande reponse a la Queue en cours"""

		if command is not None:
			self.response.append(command)

	def getResponse(self):
		"""Retourne les commandes en attente d'envoie"""

		res = self.response
		self.response = [ ]
		return res
