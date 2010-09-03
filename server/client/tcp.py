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
			if index_from == -1 and index_to == -1:
				self.buffer += data
				return [ ]
			if index_from == -1 and index_to != -1:
				frame = self.buffer + data[:index_to]
				self.buffer = None
				return [ frame ]
			if index_from != -1 and index_to == -1:
				self.buffer = data[index_from:]
				return [ ]
			if index_to > index_from:
				self.buffer = None
				pos = index_from
			if index_from > index_to:
				frame = self.buffer + data[:index_to]
				all_data.append(frame)
				self.buffer = None
				pos = index_from
		while res is not None:
			res = self.__findData(data[pos:])
			if res is not None:
				pos += len(res) + 2
				all_data.append(res)
			else:
				begin = data[pos:].find(TwistedTCPClient.DELIMITER_FROM)
				if len(data[pos:]) > 1 and begin != -1:
					self.buffer = data[pos + begin:]
				else:
					self.buffer = None
				break
		return all_data

	def dataReceived(self, data):
		""" Methode appelee lorsque l'utilisateur recoit des donnees """

		if '<policy-file-request/>' in data:
			Log().add('[TCP] Received: %s' % data)
			self.send('<!DOCTYPE cross-domain-policy SYSTEM "http://www.macromedia.com/xml/dtds/cross-domain-policy.dtd"><cross-domain-policy><allow-access-from domain="*" to-ports="*" secure="false" /></cross-domain-policy>' + "\x00", False)
		else:
			valid_data = self.__findReceived(data)
			for v_data in valid_data:
				if v_data is not None:
					commands = v_data.split("\n")
					for cmd in commands:
						if len(cmd) > 0:
							# @todo
							# Reste a savoir pourquoi on a une commande vide ici parfois ?
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

	def send(self, msg, setDelimiters = True):
		""" Methode permettant d'ecrire le message sur la socket si l'utilisateur est connecte """

		if self.connected is True:
			if setDelimiters is True:
				msg = TwistedTCPClient.DELIMITER_FROM + msg + TwistedTCPClient.DELIMITER_TO
			handle = self.transport.getHandle()
			if handle:
				handle.send(msg)

	@property
	def socket(self):
		return self.transport.getHandle()

	@property
	def isConnected(self):
		return self.transport.connected == 1
