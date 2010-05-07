from twisted.internet.protocol import Protocol
from zope.interface import implements
from commons.approval import Approval

class TwistedTCPClient(Protocol):
	def dataReceived(self, data):
		Approval().validate(data, self.dataSend)

	def dataSend(self, responses):
		for json in responses:
			self.transport.write(json + "\n")

	def connectionMade(self):
		pass

	def connectionLost(self, reason):
		self.transport.loseConnection()

	@property
	def socket(self):
		return self.transport.getHandle()

	@property
	def isConnected(self):
		return self.transport.connected == 1
