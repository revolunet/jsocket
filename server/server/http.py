##
# http.py
##

import sys
import threading
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
from twisted.python.threadpool import ThreadPool
from twisted.internet import reactor
from client.http import ClientHTTP, clientHTTP
from log.logger import Log
from config.settings import SETTINGS

class ServerHTTP(threading.Thread):
	def __init__(self, room, squeue, rqueue, client_list, http_list, session):
		self.__host = SETTINGS.SERVER_HOST
		self.__room = room
		self.__rqueue = rqueue
		self.__squeue = squeue
		self.client_list = client_list
		self.http_list = http_list
		self.session = session
		threading.Thread.__init__(self)

	def run(self):
		Log().add("[+] HTTP Server launched on %s:%d" % (self.__host, SETTINGS.SERVER_HTTP_PORT), "green")
		wsgiThreadPool = ThreadPool()
		wsgiThreadPool.start()
		resource = WSGIResource(reactor, wsgiThreadPool, clientHTTP)
		reactor.listenTCP(SETTINGS.SERVER_HTTP_PORT, Site(resource), interface=SETTINGS.SERVER_HOST)
		reactor.run()
		#client = server.Site(ClientHTTP())
		#reactor.listenTCP(SETTINGS.SERVER_HTTP_PORT, client)
		#reactor.run()
