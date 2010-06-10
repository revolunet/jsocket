##
# channel.py
##

from config.settings import SETTINGS
from commons.history import History

class Channel(object):
	"""
	Stock les informations relative aux clients presents dans les channels.
	"""

	def __init__(self, name):
		"""
		__masters: liste des admin du channel
		__users: la liste des clients presents dans le channel
		master_password: le mot de passe admin de le channel
		password: le mot de passe pour rejoindre le channel
		name: Le nom du channel
		"""

		self.__masters = []
		self.__users = []
		self.password = None
		self.master_password = SETTINGS.CHANNEL_MASTER_PASSWORD
		self.name = name
		self.history = History()

	def isMaster(self, uid):
		"""Return: si cet uid est un uid d'administrateur du channel ou non -> bool."""

		return uid in self.__masters

	def delete(self, uid):
		"""Return: Supprime un client/master du channel specifie -> bool."""

		from log.logger import Log

		if uid in self.__users:
			self.__users.remove(uid)
			Log().add("[+] Channel : client " + str(uid) + " left " + self.name)
			return True
		if uid in self.__masters:
			self.__users.remove(uid)
			Log().add("[+] Channel : master " + str(uid) + " left " + self.name)
			return True
		return False

	def add(self, uid, pwd = None):
		"""Return: Ajoute un client ou un master dans le channel specifie : -> bool."""

		from log.logger import Log

		if pwd is None and uid not in self.__users:
			self.__users.append(uid)
			Log().add("[+] Channel : client " + str(uid) + " joined " + self.name)
			return True
		elif pwd is not None and\
			pwd == self.master_password and\
			uid not in self.__masters:
			self.__masters.append(uid)
			Log().add("[+] Channel : master " + str(uid) + " joined " + self.name)
			return True
		return False

	def isProtected(self):
		"""Return: Si le channel est protege ou non -> bool."""

		return self.password is not None

	def users(self):
		"""Return : La liste des utilisateurs du Channel : -> list()"""

		return self.__users

	def masters(self):
		"""Return : La liste des masters du Channel : -> list()"""

		return self.__masters
