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

		from log.logger import Log

		while True:
			item = self.queue.get()
			Log().add('item: %s' % str(item))
			if item.get('json', None) is not None:
				for json in item['json']:
					if json['cmd'] is 'refresh':
						continue
					client = self.session.get(item['uid'])
					if client is None:
						continue
					Log().add('client: %s' % client)
					client.addResponse(self.protocol.parse(client, json))
					if callable(item.get('callback', None)):
						item['callback'](client.getResponse())
			self.queue.task_done()
