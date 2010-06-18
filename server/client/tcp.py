from twisted.internet.protocol import Protocol
from zope.interface import implements
from commons.approval import Approval
from log.logger import Log

class TwistedTCPClient(Protocol):
	"""
	Classe TCP utilisee par twisted.
	"""

	def callbackSend(self, responses):
		""" Callback appele par le :func:`WorkerParser` lorsque des reponses sont pretes """
		for json in responses:
			self.socket.send(str(json) + "\0")

	def dataReceived(self, data):
		""" Methode appelee lorsque l'utilisateur recoit des donnees """
		Log().add('[TCP] Received: %s' % data)
		if '<policy-file-request/>' in data:
			self.socket.send("<cross-domain-policy><allow-access-from domain='*' to-ports='*' secure='false' /></cross-domain-policy>" + "\0")
		else:
			commands = data.split("\n")
			for cmd in commands:
				Approval().validate(cmd, self.callbackSend)

	def connectionMade(self):
		""" Methode appelee lorsqu'un nouvel utilisateur se connecte """
		pass

	def connectionLost(self, reason):
		""" Methode appelee lorsqu'un utilisateur se deconnecte """
		self.transport.loseConnection()

	@property
	def socket(self):
		return self.transport.getHandle()

	@property
	def isConnected(self):
		return self.transport.connected == 1
