##
# http.py
##

import sys
import threading
from twisted.web import server, resource
from twisted.internet import reactor
from client.http import ClientHTTP
from log.logger import Log
from config.settings import SETTINGS

class ServerHTTP(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		Log().add("[+] HTTP Server launched on %s:%d" % (SETTINGS.SERVER_HOST, SETTINGS.SERVER_HTTP_PORT), "green")
		client = server.Site(ClientHTTP())
		reactor.listenTCP(SETTINGS.SERVER_HTTP_PORT, client, interface=SETTINGS.SERVER_HOST)
		reactor.run(installSignalHandlers=0)