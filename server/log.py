##
# log.py
##

import os
import sys
import logging
import threading
import Queue
from worker import Worker
from settings import SETTINGS

class Log(object):
	"""docstring for Log"""
	class __Log:
		def __init__(self, nb_thread = 0):
			""" Creation du fichier de log et initialisation du Queue worker """

			import os.path
			if os.path.exists(sys.path[0] + os.sep + 'log') != 1:
				os.mkdir(sys.path[0] + os.sep + 'log')
			logging.basicConfig(filename=sys.path[0] + os.sep + 'log/logs.log', format="%(asctime)s - %(message)s")
			self.__logs = logging.getLogger("server")
			self.__logs.setLevel(logging.DEBUG)
			self.__logfile = open(sys.path[0] + os.sep + 'log/logs_exception.log', 'w', 0)
			self.__logTraceback()
			self.__queue = Queue.Queue(nb_thread)
			Worker(self.__queue, 'log').start()

		def add(self, str, color = 'white'):
			""" Ajoute un element dans la queue """

			self.__queue.put([str, color])

		def get_color(self, color = 'white'):
			""" Retourne la couleur shell correspondante au parametre """

			colors = { 'white': '\033[1;37m$msg$\033[1;m',
				'red': '\033[1;31m$msg$\033[1;m',
				'yellow': '\033[1;33m$msg$\033[1;m',
				'ired': '\033[1;48m$msg$\033[1;m',
				'green': '\033[1;32m$msg$\033[1;m',
				'blue': '\033[1;34m$msg$\033[1;m' }
			return colors.get(color)

		def dprint(self, str, color = 'white'):
			""" Affiche un message sur le sortie standard et le log dans un fichier """

			if SETTINGS.IS_DEBUG:
				if 'nt' not in os.name:
					print self.get_color(color).replace('$msg$', str)
				else:
					print str
			self.__logs.debug(str)

		def __logTraceback(self):
			""" Redirige la sortie d'erreurs vers un fichier """

			try:
				sys.stderr = self.__logfile
			except Exception:
				self.add("[!] Could not redirect errors: " + str(Exception), 'ired')
		
	instance = None

	def __new__(c):
		if not Log.instance:
			Log.instance = Log.__Log()
		return Log.instance

	def __getattr__(self, attr):
		return getattr(self.instance, attr)

	def __setattr__(self, attr, val):
		return setattr(self.instance, attr, val)
