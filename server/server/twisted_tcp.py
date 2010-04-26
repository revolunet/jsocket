from log.logger import Log
from config.settings import SETTINGS
from client.twisted_tcp import TwistedTCPClient

from twisted.internet import reactor, protocol
class TwistedTCPFactory(protocol.Factory):
	protocol = TwistedTCPClient

	def __init__(self, room, rqueue, squeue, http_list, client_list):
		self.room = room
		self.rqueue = rqueue
		self.squeue = squeue
		self.http_list = http_list
		self.client_list = client_list

import threading
class ServerTCP(threading.Thread):

	def __init__(self, room, squeue, rqueue, client_list, http_list):
		self.__host = SETTINGS.SERVER_HOST
		self.__port = SETTINGS.SERVER_PORT
		Log().add("[+] TwistedTCP Server launched on %s:%d" % (self.__host, self.__port), "green")
		self.__room = room
		self.__init_queues(squeue, rqueue)
		self.client_list = client_list
		self.http_list = http_list
		threading.Thread.__init__(self)

	def __init_queues(self, squeue, rqueue):
		""" Initialise les queues d'envoie et reception (parsing) de message client """

		self.__squeue = squeue
		self.__rqueue = rqueue

	def run(self):
		factory = protocol.ServerFactory()
		reactor.listenTCP(self.__port, TwistedTCPFactory(self.__room, self.__rqueue, self.__squeue, self.http_list, self.client_list), interface=self.__host)
		reactor.run(installSignalHandlers=0)
