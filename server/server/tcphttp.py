from log.logger import Log
from config.settings import SETTINGS
from client.tcp import TwistedTCPClient
from client.http import ClientHTTP

from twisted.web import server, resource
from twisted.internet import reactor, protocol
class TwistedTCPFactory(protocol.Factory):
	protocol = TwistedTCPClient

import threading
class ServerTwisted(threading.Thread):

	def __init__(self):
		self.__host = SETTINGS.SERVER_HOST
		self.__port = SETTINGS.SERVER_PORT
		Log().add("[+] TwistedTCP Server launched on %s:%d" % (self.__host, self.__port), "green")
		threading.Thread.__init__(self)

	def run(self):
		factory = protocol.ServerFactory()
		reactor.listenTCP(self.__port, TwistedTCPFactory(), interface=self.__host)

		Log().add("[+] HTTP Server launched on %s:%d" % (SETTINGS.SERVER_HOST, SETTINGS.SERVER_HTTP_PORT), "green")
		client = server.Site(ClientHTTP())
		reactor.listenTCP(SETTINGS.SERVER_HTTP_PORT, client, interface=SETTINGS.SERVER_HOST)

		reactor.run(installSignalHandlers=0)
