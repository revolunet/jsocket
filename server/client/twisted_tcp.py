from twisted.internet.protocol import Protocol
from zope.interface import implements
from commons.approval import Approval

class TwistedTCPClient(Protocol):
	def dataReceived(self, data):
		Approval().validate(data, self.dataSend)
		
	def dataSend(self, data):
		self.transport.write(data)

	def connectionMade(self):
		print "[+] New TCP Client !"

	def connectionLost(self, reason):
		print "[+] Delete TCP Client"

	@property
	def socket(self):
		return self.transport.getHandle()

	@property
	def isConnected(self):
		return self.transport.connected == 1