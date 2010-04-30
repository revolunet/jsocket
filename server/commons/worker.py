##
# worker.py
##

import threading
import Queue
import time
from jexception import JException

class WorkerLog(threading.Thread):
	"""
	Gestion de l'affichage des logs
	"""

	def __init__(self, queue):
		self.__queue = queue
		threading.Thread.__init__(self)

	def run(self):
		""" Redirection vers la methode approprie pour le traitement de la Queue """

		from log.logger import Log
		while True:
			item = self.__queue.get()
			Log().dprint(item[0], item[1])
			self.__queue.task_done()

class WorkerSend(threading.Thread):
	"""
	Gestion d'envoie du json au client
	"""

	def __init__(self, queue):
		self.__queue = queue
		threading.Thread.__init__(self)

	def run(self):
		""" Parcours de la liste pour envoyer les requetes correspondantes """

		while True:
			item = self.__queue.get()
			if item.get('client', None) is not None:
				if item['type'] == 'tcp':
					try:
						if item.get('data', None) is not None and len(item.get('data')) > 0:
							if item.get('client').client_socket is not None:
								item.get('client').client_socket.send(item.get('data') + "\0")
					except Exception:
						Log().add(JException().formatExceptionInfo())
						Log().add("[DEBUG] failed to send %s" % item['data'])
				elif item['type'] == 'http':
					try:
						if item.get('data', None) is not None and len(item.get('data')) > 0:
							if item.get('client').unique_key not in item.get('client').http_list:
								item.get('client').http_list[item.get('client').unique_key] = [ ]
							item.get('client').http_list[item.get('client').unique_key].append(item.get('data'))
					except Exception:
						Log().add(JException().formatExceptionInfo())
						Log().add("[DEBUG] failed to send %s" % item['data'])
				self.__queue.task_done()

class WorkerReceive(threading.Thread):
	"""
 	Gestion de reception des commandes json des clients
	"""

	def __init__(self, queue):
		self.__queue = queue
		threading.Thread.__init__(self)

	def run(self):
		""" Parcours la Queue pour parser la string correspondante """

		from client.tcp import ClientTCP
		from log.logger import Log
		while True:
			item = self.__queue.get()
			commands = item['data'].split("\n")
			if item['type'] == 'tcp':
				if len(commands) == 1:
					item['client'].protocol.parse(item['data'])
					item['client'].last_action = int(time.time())
				else:
					for cmd in commands:
						item['client'].protocol.parse(cmd)
						item['client'].last_action = int(time.time())
			elif item['type'] == 'http':
				try:
					http_buffer = ""
					if len(commands) == 1:
						item.get('client').protocol.parse(commands[0])
						item.get('client').last_action = int(time.time())
						item.get('client').updateSession(item.get('client').unique_key)
					else:
						for cmd in commands:
							item.get('client').protocol.parse(cmd)
							item.get('client').last_action = int(time.time())
							item.get('client').updateSession(item.get('client').unique_key)
					item.get('client').disconnection()
				except Exception as e:
					Log().add(e)
					Log().add("[DEBUG] failed to send %s" % item['data'])
			self.__queue.task_done()
