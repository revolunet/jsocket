##
# worker.py
##

import threading


class WorkerLog(threading.Thread):
	""" Gestion de l'affichage des logs """

	def __init__(self, queue):
		self.__queue = queue
		threading.Thread.__init__(self)
		self.setDaemon(True)

	def run(self):
		""" Affichage des donnees via Log() """

		from log.logger import Log

		while True:
			item = self.__queue.get()
			Log().dprint(item[0], item[1])
			self.__queue.task_done()

class WorkerParser(threading.Thread):
	""" Gestion du traitement des commandes json """

	def __init__(self, queue, session, protocol):
		self.queue = queue
		self.session = session
		self.protocol = protocol
		threading.Thread.__init__(self)
		self.setDaemon(True)

	def run(self):
		""" Traitement des commandes json """

		from log.logger import Log
		from twisted.internet import reactor

		while True:
			item = self.queue.get()
			if item.get('json', None) is not None:
				for json in item['json']:
					if json['cmd'] is 'refresh':
						continue
					client = self.session.get(item['uid'])
					if client is None:
						continue
					if item.get('type', None) is not None:
						client.type = item['type']
					client.addResponse(self.protocol.parse(client, json))
					if callable(item.get('callback', None)):
						reactor.callFromThread(item['callback'], client.getResponse())
			self.queue.task_done()
