import datetime

from server.websocket import WebSocketHandler
from commons.approval import Approval
from commons.session import Session
from log.logger import Log

class ClientWebSocket(WebSocketHandler):
	"""
	Classe WebSocket HTML5 utilisee par twisted
	"""

	def __init__(self, transport):
		self.uid = None
		self.connected = False
		WebSocketHandler.__init__(self, transport)

	def callbackSend(self, responses):
		""" Callback appele par le :func:`WorkerParser` lorsque des reponses sont pretes """

		for json in responses:
			if '{"from": "connected",' not in json:
				self.send(json)

	def frameReceived(self, frame):
		""" Methode appelee lorsque l'utilisateur recoit des donnees """

		Log().add('[WebSocket] Received: %s' % frame)
		self.connected = True
		commands = frame.split("\n")
		for cmd in commands:
			if '{"cmd": "connected", "args": "null"' in cmd:
				uid = Approval().validate(cmd, None, 'websocket')
				if uid is not None:
					self.uid = uid
				self.send('{"from": "connected", "value": "%s"}' % uid)
			else:
				Approval().validate(cmd, self.callbackSend)

	def connectionLost(self, reason):
		""" Methode appelee lorsqu'un utilisateur se deconnecte """

		self.connected = False
		if self.uid is not None:
			Log().add('[WebSocket] Logout %s' % str(self.uid))
			Session().delete(self.uid)
		self.transport.loseConnection()

	def send(self, msg):
		""" Methode permettant d'ecrire le message sur la socket si l'utilisateur est connecte """

		if self.connected is True:
			self.transport.write(msg)
