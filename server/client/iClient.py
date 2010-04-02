
import threading
import datetime
import random
from config.settings import SETTINGS
from commons.protocol import Protocol

class IClient(threading.Thread):
	"""
	Interface commune aux clients TCP et HTTP.
	Regroupe les informations qui caracterise un client.
	"""

	def __init__(self, room, rqueue, squeue, Ctype, http_list):
		"""
		HTTP/TCP Client constructeur.
		room: la liste des salons disponnible sur le serveur.
		rqueue: la queue de lecture.
		squeue: la queue d'envoie.
		Ctype: HTTP/TCP definie le type de client.
		http_list: Liste des retours de commandes.
		"""
		
		self.protocol = Protocol(self)
		self.type = Ctype
		self.room = room
		self.master = False
		self.nickName = None
		self.master_password = SETTINGS.MASTER_PASSWORD
		self.unique_key = hex(random.getrandbits(64))
		self.rqueue = rqueue
		self.squeue = squeue
		self.status = 'online'
		self.connection_time = datetime.datetime.now()
		self.last_action = self.connection_time
		self.room_name = None
		self.http_list = http_list
		threading.Thread.__init__(self)

	def sput(self, data):
		"""
		On ajoute des data dans la squeue du client.
		"""
		
		self.squeue.put( { 'type': self.type, 'data': data, 'client': self } )
	
	def rput(self, data):
		"""
		On ajoute des data dans la rqueue du client.
		"""
		
		self.rqueue.put( { 'type': self.type, 'data': data, 'client': self } )
