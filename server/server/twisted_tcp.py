from log.logger import Log
from config.settings import SETTINGS
from client.twisted_tcp import TwistedTCPClient

from twisted.internet import reactor, protocol
class TwistedTCPFactory(protocol.Factory):
	protocol = TwistedTCPClient

import threading
class ServerTCP(threading.Thread):

	def __init__(self):
		self.__host = SETTINGS.SERVER_HOST
		self.__port = SETTINGS.SERVER_PORT
		Log().add("[+] TwistedTCP Server launched on %s:%d" % (self.__host, self.__port), "green")
		threading.Thread.__init__(self)

	def run(self):
		factory = protocol.ServerFactory()
		reactor.listenTCP(self.__port, TwistedTCPFactory(), interface=self.__host)
		reactor.run(installSignalHandlers=0)
