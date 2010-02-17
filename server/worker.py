##
# worker.py
##

import threading
import Queue

class Worker(threading.Thread):
	"""docstring for Worker"""
	def __init__(self, queue, type = 'log'):
		self.__queue = queue
		self.__type = type
		threading.Thread.__init__(self)

	def type_log(self):
		""" Parcours la Queue pour y logger tous ces elements via Log """

		from log import Log
		while True:
			item = self.__queue.get()
			Log().dprint(item[0], item[1])

	def type_send(self):
		""" Parcours la Queue pour envoyer la string correspondante a l'objet client """
		
		from client import Client
		while True:
			item = self.__queue.get()
			try:
				item[0].client.client_socket.send(item[1] + "\0")
			except Exception:
				pass
		
	def type_recv(self):
		""" Parcours la Queue pour parser la string correspondante """
		
		from client import Client
		while True:
			item = self.__queue.get()
			commands = item[1].split("\n")
			for cmd in commands:
				item[0].protocol.parse(cmd)

	def run(self):
		""" Redirection vers la methode approprie pour le traitement de la Queue """

		try:
			method = getattr(self, 'type_' + self.__type, None)
		except AttributeError:
			from log import Log
			Log().add("[!] Method %s of worker does not exists", 'ired')
		if callable(method):
			method()