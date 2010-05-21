import datetime

from server.websocket import BasicOperations
from commons.approval import Approval
from log.logger import Log

class ClientWebSocket(BasicOperations):
	"""
	Classe WebSocket HTML5 utilisee par twisted
	"""

	def dataSend(self, responses):
		""" Callback appele par le :func:`WorkerParser` lorsque des reponses sont pretes """
		for json in responses:
			self.send(json)

	def on_read(self, line):
		""" Methode appelee lorsque l'utilisateur recoit des donnees """
		Log().add('[+] Send: %s' % line, 'green')
		#Approval().validate(line, self.dataSend)
		self.send(line)

	def on_connect(self):
		""" Methode appelee lorsqu'un nouvel utilisateur se connecte """
		pass

	def on_close(self, r):
		""" Methode appelee lorsqu'un utilisateur se deconnecte """
		pass

	def after_connection(self):
		""" Methode appelee lorsqu'un utilisateur est connecte """
		pass
