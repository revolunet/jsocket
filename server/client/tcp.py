from twisted.internet.protocol import Protocol
from zope.interface import implements
from commons.session import Session
from commons.approval import Approval
from log.logger import Log

class TwistedTCPClient(Protocol):
	"""
	Classe TCP utilisee par twisted.
	"""

	def __init__(self):
		self.uid = None

	def callbackSend(self, responses):
		""" Callback appele par le :func:`WorkerParser` lorsque des reponses sont pretes """
		for json in responses:
			self.transport.getHandle().send(str(json) + "\0")

	def dataReceived(self, data):
		""" Methode appelee lorsque l'utilisateur recoit des donnees """
		Log().add('[TCP] Received: %s' % data)
		if '<policy-file-request/>' in data:
			self.transport.getHandle().send("<cross-domain-policy><allow-access-from domain='*' to-ports='*' secure='false' /></cross-domain-policy>" + "\0")
		else:
			commands = data.split("\n")
			for cmd in commands:
				uid = Approval().validate(cmd, self.callbackSend)
				if uid is not None:
					self.uid = uid

	def connectionMade(self):
		""" Methode appelee lorsqu'un nouvel utilisateur se connecte """
		self.uid = None

	def connectionLost(self, reason):
		""" Methode appelee lorsqu'un utilisateur se deconnecte """
		Log().add('[ConnectionLost] %s' % str(self.uid))
		if self.uid is not None:
			Session().delete(self.uid)
		self.transport.loseConnection()

	@property
	def socket(self):
		return self.transport.getHandle()

	@property
	def isConnected(self):
		return self.transport.connected == 1
