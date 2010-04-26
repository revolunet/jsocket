from twisted.internet.protocol import Protocol
from zope.interface import implements
from client.iClient import IClient

class TwistedTCPClient(Protocol):
	def dataReceived(self, data):
		print "[+] Client write: %s " % str(data)
		
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
		
	@property
	def room(self):
		return self.factory.room
		
	@property
	def rqueue(self):
		return self.factory.rqueue
	
	@property
	def squeue(self):
		return self.factory.squeue
	
	@property
	def http_list(self):
		return self.factory.http_list
	
	@property
	def client_list(self):
		return self.factory.client_list