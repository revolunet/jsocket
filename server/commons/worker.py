##
# worker.py
##

import threading
import Queue
import time
from commons.session import Session
from commons.protocol import Protocol
from jexception import JException

class WorkerLog(threading.Thread):
	""" Gestion de l'affichage des logs """

	def __init__(self, queue):
		self.__queue = queue
		threading.Thread.__init__(self)

	def run(self):
		""" Affichage des donnees via Log() """

		from log.logger import Log
		while True:
			item = self.__queue.get()
			Log().dprint(item[0], item[1])
			self.__queue.task_done()

class WorkerParser(threading.Thread):
	""" Gestion du traitement des commandes json """

	def __init__(self, queue):
		self.queue = queue
		self.session = Session()
		self.protocol = Protocol()
		threading.Thread.__init__(self)

	def run(self):
		""" Traitement des commandes json """

		while True:
			item = self.__queue.get()
			if item.get('json', None) is not None:
				client = None
				for json in item['json']:
					if client is None:
						client = self.session.getFromJson(json)
					client.addResponse(self.protocol.parse(client, json))
					if callable(item.get('callback', None)):
						item['callback'](client.getResponse())
			self.queue.task_done()
