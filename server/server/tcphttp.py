import threading

from log.logger import Log
from config.settings import SETTINGS
from client.tcp import TwistedTCPClient
from client.http import ClientHTTP
from client.websocket import ClientWebSocket
from server.websocket import WebSocketFactory

from twisted.web import server, resource
from twisted.internet import reactor, protocol

class TwistedTCPFactory(protocol.Factory):
	protocol = TwistedTCPClient

class ServerTwisted(threading.Thread):

	def __init__(self):
		self.__host = SETTINGS.SERVER_HOST
		self.__port = SETTINGS.SERVER_PORT
		threading.Thread.__init__(self)

	def run(self):
		# TCP Server
		Log().add("[+] TwistedTCP Server launched on %s:%d" % (self.__host, self.__port), "green")
		factory = protocol.ServerFactory()
		reactor.listenTCP(self.__port, TwistedTCPFactory(), interface=self.__host)

		# WebSocket HTML5 Server
		Log().add("[+] WebSocket HTML5 Server launched on %s:%s" % (SETTINGS.SERVER_HOST, SETTINGS.SERVER_WEBSOCKET_PORT), "green")
		webSocketFactory = WebSocketFactory(ClientWebSocket())
		reactor.listenTCP(SETTINGS.SERVER_WEBSOCKET_PORT, webSocketFactory)

		# HTTP Server
		Log().add("[+] HTTP Server launched on %s:%d" % (SETTINGS.SERVER_HOST, SETTINGS.SERVER_HTTP_PORT), "green")
		client = server.Site(ClientHTTP())
		reactor.listenTCP(SETTINGS.SERVER_HTTP_PORT, client, interface=SETTINGS.SERVER_HOST)

		# Running servers
		reactor.run(installSignalHandlers=0)
