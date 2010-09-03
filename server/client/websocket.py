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
		WebSocketHandler.__init__(self, transport)
		self.transport.uid = None
		self.transport.connected = False

	def callbackSend(self, responses):
		""" Callback appele par le :func:`WorkerParser` lorsque des reponses sont pretes """

		if responses is None:
			return False
		for json in responses:
			if json is not None and len(json) and '{"from": "connected",' not in json:
				self.send(json)
		return True

	def frameReceived(self, frame):
		""" Methode appelee lorsque l'utilisateur recoit des donnees """

		Log().add('[WebSocket] Received: %s' % frame)
		self.transport.connected = True
		commands = frame.split("\n")
		uid = None
		for cmd in commands:
			if '{"cmd": "connected", "args": "null"' in cmd:
				uid = Approval().validate(cmd, self.callbackSend, 'websocket')
				self.send('{"from": "connected", "value": "%s"}' % uid)
			elif len(cmd) > 0:
				uid = Approval().validate(cmd, self.callbackSend, 'websocket')
			if uid is not None:
				self.transport.uid = uid

	def connectionLost(self, reason):
		""" Methode appelee lorsqu'un utilisateur se deconnecte """

		self.transport.connected = False
		if self.transport.uid is not None:
			Log().add('[WebSocket] Logout %s' % str(self.transport.uid))
			Session().delete(self.transport.uid)
		self.transport.loseConnection()

	def send(self, msg):
		""" Methode permettant d'ecrire le message sur la socket si l'utilisateur est connecte """

		if self.transport.connected is True:
			self.transport.write(msg)

	@property
	def socket(self):
		return self.transport.getHandle()
