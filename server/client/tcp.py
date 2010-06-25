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
		self.connected = False

	def callbackSend(self, responses):
		""" Callback appele par le :func:`WorkerParser` lorsque des reponses sont pretes """

		for json in responses:
			self.send(str(json))

	def dataReceived(self, data):
		""" Methode appelee lorsque l'utilisateur recoit des donnees """

		Log().add('[TCP] Received: %s' % data)
		if '<policy-file-request/>' in data:
			self.send('<!DOCTYPE cross-domain-policy SYSTEM "http://www.macromedia.com/xml/dtds/cross-domain-policy.dtd"><cross-domain-policy><allow-access-from domain="*" to-ports="*" secure="false" /></cross-domain-policy>')
		else:
			commands = data.split("\n")
			for cmd in commands:
				uid = Approval().validate(cmd, self.callbackSend)
				if uid is not None:
					self.uid = uid

	def connectionMade(self):
		""" Methode appelee lorsqu'un nouvel utilisateur se connecte """

		self.uid = None
		self.connected = True

	def connectionLost(self, reason):
		""" Methode appelee lorsqu'un utilisateur se deconnecte """

		self.connected = False
		if self.uid is not None:
			Log().add('[TCP] Logout %s' % str(self.uid))
			Session().delete(self.uid)
		self.transport.loseConnection()

	def send(self, msg):
		""" Methode permettant d'ecrire le message sur la socket si l'utilisateur est connecte """

		if self.connected is True:
			self.transport.getHandle().send(msg + "\0")

	@property
	def socket(self):
		return self.transport.getHandle()

	@property
	def isConnected(self):
		return self.transport.connected == 1
