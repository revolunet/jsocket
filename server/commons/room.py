##
# room.py
##

import simplejson
from commons.protocol import Protocol
from config.settings import SETTINGS
from commons.channel import Channel
from commons.filter import Filter

class Room(object):
	"""
	Liste des channels disponnible sur le server.
	"""

	def __init__(self):
		self.applications = {}
		self.init_app()
		self.filter = Filter()

	def merge(self, list1, list2):
		""" Merge deux list ensemble """
		for s in list2:
			if s not in list1:
				list1.append(s)
		return list1

	def init_app(self):
		"""Initialise les applications par defaut."""

		for app in SETTINGS.STARTUP_APP:
			if app.get('app') not in self.applications:
				self.applications[app.get('app')] = []
			self.applications[app.get('app')].append({
				'name': app.get('name'),
				'channel': Channel(app.get('name')),
				'app': app.get('app')
			})

	def list_users(self, channelName, appName = None):
		"""Return : la liste de tous les utilisateurs du serveur ou d'une application -> list(Client) """

		if appName in self.applications and self.chanExists(channelName=channelName, appName=appName):
			channel = self.Channel(channelName=channelName, appName=appName)
			if channel is not None:
				return channel.users()
		users = []
		for app in self.applications:
			for c in self.applications[app]:
				self.merge(users, c.get('object').users())
		return users

	def create(self, channelName, uid, appName, password = None):
		"""Return: Ajoute un channel a la liste des rooms  -> bool"""

		import random
		from commons.session import Session

		if appName not in self.applications:
			self.applications[appName] = []

		if self.chanExists(channelName=channelName, appName=appName) == False:
			client = Session().get(uid)
			client.room_name = channelName
			channel = Channel(channelName)
			channel.master_password = random.getrandbits(16)
			channel.add(uid, channel.master_password)
			if password is not None:
				channel.password = password
			self.applications[appName].append({
				'name': channelName,
				'channel': channel,
				'app': appName
			})
			return True
		#self.applications.pop(appName)
		return False

	def remove(self, channelName, appName):
		"""Return: Supprime un channel de la liste des rooms -> bool """

		if appName in self.applications:
			for idx, channel in enumerate(self.applications[appName]):
				if channel.get('name') == channelName:
					self.applications[appName].pop(idx)
					return True
		return False

	def join(self, channelName, appName, uid, password = None):
		"""Return: Ajoute un utilisateur dans la room specifie  -> bool """

		if self.chanExists(channelName=channelName, appName=appName) is False:
			return False
		channel = self.Channel(channelName=channelName, appName=appName)
		if password is not None:
			if channel.password != password:
				return False
		channel.add(uid)
		return True

	def part(self, channelName, appName, uid):
		"""Return Supprime un utilisateur d'une room  -> bool """

		if self.chanExists(channelName=channelName, appName=appName) is False:
			return False
		channel = self.Channel(channelName=channelName, appName=appName)
		return channel.delete(uid)

	def leaveRooms(self, uid):
		from commons.session import Session
		
		client = Session().get(uid)
		for application in self.applications:
			for c in self.applications[application]:
				channel = c.get('channel')
				if channel is not None:
					if client is not None:
						self.status(client, application, channel.name)
					channel.delete(uid)

	def Channel(self, channelName, appName):
		if appName in self.applications:
			for c in self.applications[appName]:
				if c.get('name') == channelName:
					return c.get('channel')
		return None

	def Application(self, appName):
		"""Return : l'application specifie -> Application """

		if appName in self.applications:
			return self.applications[appName]
		return None

	def forward(self, channelName, appName, commande, uid, app):
		"""Return : Envoie une commande a tous les utilisateurs d'une application -> bool """

		from commons.session import Session
		from log.logger import Log

		if self.chanExists(channelName=channelName, appName=appName):
			channel = self.Channel(channelName=channelName, appName=appName)

			if uid in channel.masters():
				users = channel.users()
				master = Session().get(uid)
				json = Protocol.forgeJSON('forward', '["' + master.getName() + '", "' + commande + '"]',
										  {'channel': channelName, 'app': appName, 'toUid': uid})
				channel.history.add(uid, json)
				for u in users:
					user = Session().get(u)
					if user is not None:
						user.addResponse(json)
				if len(users) > 1:
					return True
		return False

	def history(self, channelName, appName):

		if self.chanExists(channelName=channelName, appName=appName):
			channel = self.Channel(channelName=channelName, appName=appName)
			return self.filter.Run(channel.history.get())
		return []

	def message(self, channelName, appName, sender, users, message):
		"""Return : Envoie un message a une liste d'utilisateurs -> bool """

		if self.chanExists(channelName=channelName, appName=appName):
			if len(users) > 0:
				channel = self.Channel(channelName=channelName, appName=appName)
				if users[0] == 'master' and sender in channel.users():
					masters = channel.masters()
					for master in masters:
						self.__sendMessage(channelName, appName, sender, master, message)
					return True
				list_users = channel.users()
				list_masters = channel.masters()
				list_users = self.merge(list_users, list_masters)
				if len(list_users) >= 1:
					if users[0] == 'all':
						for u in list_users:
							if sender is not u:
								self.__sendMessage(channelName, appName, sender, u, message)
						return True
					for user in list_users:
						if user in users:
							self.__sendMessage(channelName, appName, sender, user, message)
					return True
		return False

	def appAuth(self, channelName, appName, password, uid):
		"""Return : Auth un utilisateur sur une application -> bool """

		if self.chanExists(channelName=channelName, appName=appName):
			channel = self.Channel(channelName, appName)
			return channel.add(uid, password)
		return False

	def changeAppMasterPwd(self, channelName, appName, password):
		"""Return: change le mot de passe admin d'une application -> bool """

		if self.chanExists(channelName=channelName, appName=appName):
			channel = self.Channel(channelName, appName)
			channel.master_password = password
			return True
		return False

	def appExists(self, appName):
		"""Return: Si une application existe ou non -> bool."""

		return appName in self.applications

	def chanExists(self, channelName, appName):

		if appName in self.applications:
			for c in self.applications[appName]:
				if c.get('name') == channelName:
					return True
		return False
		
	def status(self, client, appName, channelName):
		from log.logger import Log
		from commons.session import Session
		
		if self.chanExists(channelName=channelName, appName=appName):
			channel = self.Channel(channelName, appName)
			key = client.unique_key
			name = client.getName()
			to_send = {"name": name, "key": key, "status": 'offline'}
			masters = channel.masters()
			for master in masters:
				m = Session().get(master)
				if m is not None:
					Log().add("[+] Client : envoie du status de " + name + " vers l'utilisateur : " + m.getName())
					json = Protocol.forgeJSON('status', simplejson.JSONEncoder().encode(to_send), {'channel': channel.name})
					m.addResponse(json)

	def __sendMessage(self, channelName, appName, sender, to, message):
		"""Fromate le json, et envoie le message a l'utilisateur"""

		from commons.session import Session

		sender = Session().get(sender)
		receiver =  Session().get(to)
		json = Protocol.forgeJSON('message', '["' + sender.getName() + '", "' + message + '"]',
											  {'channel': channelName, 'app': appName})
		if receiver is not None:
			receiver.addResponse(json)
