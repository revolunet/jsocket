from twisted.internet.protocol import Protocol
from zope.interface import implements
from commons.session import Session
from commons.approval import Approval
from log.logger import Log

class TwistedTCPClient(Protocol):
	"""
	Classe TCP utilisee par twisted.
	"""

	DELIMITER_FROM = "\x00"
	DELIMITER_TO = "\xff"

	def __init__(self):
		self.uid = None
		self.connected = False
		self.buffer = None

	def callbackSend(self, responses):
		""" Callback appele par le :func:`WorkerParser` lorsque des reponses sont pretes """

		for json in responses:
			self.send(str(json))
			
	def __findData(self, data):
		index_from = data.find(TwistedTCPClient.DELIMITER_FROM)
		index_to = data.find(TwistedTCPClient.DELIMITER_TO)
		if index_from != -1 and index_to != -1:
			return data[index_from + 1 : index_to]
		return None
		
	def __findReceived(self, data):
		all_data = []
		
		pos = 0
		res = ''
		if self.buffer is not None:
			index_to = data.find(TwistedTCPClient.DELIMITER_TO)
			index_from = data.find(TwistedTCPClient.DELIMITER_FROM)
			if index_to != -1:
				if index_from == -1:
					self.buffer = "%s%s" % (self.buffer, data[:index_to])
					all_data.append(self.buffer)
					self.buffer = None
					return all_data
				elif index_from != -1 and index_to < index_from:
					self.buffer = "%s%s" % (self.buffer, data[:index_to])
					all_data.append(self.buffer)
					self.buffer = None
					pos = index_from
				else:
					self.buffer = None
			else:
				self.buffer = None
		while res is not None:
			res = self.__findData(data[pos:])
			if res is not None:
				pos = data[pos:].find(TwistedTCPClient.DELIMITER_TO + 1)
				all_data.append(res)
			else:
				if data[pos] == TwistedTCPClient.DELIMITER_FROM:
					self.buffer = data[pos + 1:]
		return all_data

	def dataReceived(self, data):
		""" Methode appelee lorsque l'utilisateur recoit des donnees """

		#print repr(data)
		if '<policy-file-request/>' in data:
			Log().add('[TCP] Received: %s' % data)
			self.send('<!DOCTYPE cross-domain-policy SYSTEM "http://www.macromedia.com/xml/dtds/cross-domain-policy.dtd"><cross-domain-policy><allow-access-from domain="*" to-ports="*" secure="false" /></cross-domain-policy>')
		else:
			valid_data = self.__findReceived(data)
			for v_data in valid_data:
				if v_data is not None:
					commands = v_data.split("\n")
					for cmd in commands:
						Log().add('[TCP] Received: %s' % cmd)
						uid = Approval().validate(cmd, self.callbackSend, 'tcp')
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
