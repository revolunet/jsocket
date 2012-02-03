import threading

from log.logger import Log
from config.settings import SETTINGS
from client.tcp import TwistedTCPClient
from client.http import ClientHTTP
from server.websocket import WebSocketSite
from client.websocket import ClientWebSocket

from twisted.web import server
from twisted.internet import reactor, protocol
from twisted.web.static import File


class TwistedTCPFactory(protocol.Factory):
    protocol = TwistedTCPClient

class FileNoListing(File):
	def directoryListing(self):
		return None

class ServerTwisted(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # TCP Server
        Log().add("[+] TwistedTCP Server launched on %s:%d" %
                  (SETTINGS.SERVER_HOST, SETTINGS.SERVER_PORT), "green")
        reactor.listenTCP(SETTINGS.SERVER_PORT, TwistedTCPFactory(),
                          interface=SETTINGS.SERVER_HOST)

        # WebSocket HTML5 Server
        Log().add("[+] WebSocket HTML5 Server launched on %s:%s" %
                  (SETTINGS.SERVER_HOST, SETTINGS.SERVER_WEBSOCKET_PORT),
                  "green")
        root = FileNoListing(".")
        site = WebSocketSite(root)
        site.addHandler('/jsocket', ClientWebSocket)
        reactor.listenTCP(SETTINGS.SERVER_WEBSOCKET_PORT, site,
                          interface=SETTINGS.SERVER_HOST)

        # HTTP Server
        Log().add("[+] HTTP Server launched on %s:%d" %
                  (SETTINGS.SERVER_HOST, SETTINGS.SERVER_HTTP_PORT), "green")
        client = server.Site(ClientHTTP())
        reactor.listenTCP(SETTINGS.SERVER_HTTP_PORT, client,
                          interface=SETTINGS.SERVER_HOST)

        # Running servers
        reactor.run(installSignalHandlers=0)
