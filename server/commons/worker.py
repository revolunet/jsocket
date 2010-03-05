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

		from log.logger import Log
		while True:
			item = self.__queue.get()
			Log().dprint(item[0], item[1])
			self.__queue.task_done()

	def type_send(self):
		""" Parcours la Queue pour envoyer la string correspondante a l'objet client """
		
		from client.tcp import ClientTCP
		from log.logger import Log
		while True:
			item = self.__queue.get()
			if item['type'] == 'tcp':
				try:
					item['client'].client_socket.send(item['data'] + "\0")
					#Log().add("[DEBUG] (%s) send: %s" % (str(item[0]), item[1]))
				except Exception:
					Log().add("[DEBUG] failed to send %s" % item['data'])
			elif item['type'] == 'http':
				pass
			else:
				pass
			self.__queue.task_done()
		
	def type_recv(self):
		""" Parcours la Queue pour parser la string correspondante """
		
		from client.tcp import ClientTCP
		while True:
			item = self.__queue.get()
			commands = item['data'].split("\n")
			if item['type'] == 'tcp':
				if len(commands) == 1:
					item['client'].protocol.parse(item['data'])
				else:
					for cmd in commands:
						item['client'].rput(cmd)
			elif item['type'] == 'http':
				pass
			else:
				pass
			self.__queue.task_done()

	def run(self):
		""" Redirection vers la methode approprie pour le traitement de la Queue """

		try:
			method = getattr(self, 'type_' + self.__type, None)
		except AttributeError:
			from log import Log
			Log().add("[!] Method %s of worker does not exists", 'ired')
		if callable(method):
			method()
