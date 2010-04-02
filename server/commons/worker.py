##
# worker.py
##

import threading
import Queue
from jexception import JException

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
							print "Added data %s for client %s" % (item.get('data'), item.get('client').unique_key)
					except Exception:
						Log().add(JException().formatExceptionInfo())
						Log().add("[DEBUG] failed to send %s" % item['data'])
				else:
					pass
				self.__queue.task_done()
		
	def type_recv(self):
		""" Parcours la Queue pour parser la string correspondante """
		
		from client.tcp import ClientTCP
		from log.logger import Log
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
				try:
					http_buffer = ""
					if len(commands) == 1:
						item.get('client').protocol.parse(commands[0])
						#item.get('client').http_list[item.get('client').unique_key].append(commands[0])
					else:
						for cmd in commands:
							item['client'].rput(cmd)
							#item.get('client').http_list[item.get('client').unique_key].append(cmd)
					#if item.get('client').unique_key in item.get('client').http_list:
					#	if len(item.get('client').http_list[item.get('client').unique_key]) > 0:
					#		for cmd in item.get('client').http_list[item.get('client').unique_key]:
					#			if item.get('client').client_socket is None:
					#				print "Client deco ! socket is None"
					#				item.get('client').disconnection()
					#			else:
					#				http_buffer += cmd + "\n"
					#		if item.get('client').client_socket is not None:
					#			print "SENDING %s" % http_buffer
					#			item.get('client').client_socket.send(http_buffer)
					#			item.get('client').http_list[item.get('client').unique_key] = [ ]
								
					item.get('client').disconnection()
				except Exception as e:
					Log().add(e)
					Log().add("[DEBUG] failed to send %s" % item['data'])
			else:
				pass
			self.__queue.task_done()

	def run(self):
		""" Redirection vers la methode approprie pour le traitement de la Queue """

		from log.logger import Log
		try:
			method = getattr(self, 'type_' + self.__type, None)
		except AttributeError:
			Log().add(JException().formatExceptionInfo())
			Log().add("[!] Method %s of worker does not exists", 'ired')
		if callable(method):
			method()
