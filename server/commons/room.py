##
# room.py
##

from commons.protocol import Protocol
from config.settings import SETTINGS
from commons.channel import Channel

class Room(object):
	"""
	Liste des channels disponnible sur le server.
	"""
	
	def __init__(self):
		self.applications = {}
		self.init_app()
		
	def init_app(self):
		"""Initialise les applications par defaut."""
		
		for app in SETTINGS.STARTUP_APP:
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
		from heapq import merge
		users = []
		for app in self.applications:
			for c in self.applications[app]:
				users = list(merge(users, c.get('object').users()))
		return users
		
	def create(self, channelName, uid, appName, password = None):
		"""Return: Ajoute un channel a la liste des rooms  -> bool"""
		
		import random
		
		if appName not in self.applications:
			self.applications[appName] = []
		if self.chanExists(channelName=channelName, appName=appName) == False:
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
		self.applications.pop(appName)
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
		channel.delete(uid)
		return True
		
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
		
		if self.chanExists(channelName=channelName, appName=appName):
			channel = self.Channel(channelName=channelName, appName=appName)
			
			if uid in channel.masters():
				users = channel.users()
				master = Session().get(uid)
				json = Protocol.forgeJSON('forward', '["' + master.getName() + '", "' + commande + '"]',
													  {'channel': channelName, 'app': appName})
				for u in users:
					user = Session().get(u)
					user.addResponse(json)
				if len(users) > 1:
					return True
		return False
		
	def message(self, channelName, appName, sender, users, message):
		"""Return : Envoie un message a une liste d'utilisateurs -> bool """
		
		if self.chanExists(channelName=channelName, appName=appName):
			if len(users) > 0:
				channel = self.Channel(channelName=channelName, appName=appName)
				if users[0] == 'master' and sender in channel.masters():
					masters = channel.masters()
					for master in masters:
						self.__sendMessage(channelName, appName, sender, master, message)
					return True
				list_users = channel.users()
				if len(list_users) >= 1:
					if users[0] == 'all':
						for u in list_users:
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
			channel = Channel(channelName)
			return channel.add(uid, password)
		return False
	
	def changeAppMasterPwd(self, channelName, appName, password):
		"""Return: change le mot de passe admin d'une application -> bool """
		
		if self.chanExists(channelName=channelName, appName=appName):
			channel = Channel(channelName)
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
		
	def __sendMessage(self, channelName, appName, sender, to, message):
		"""Fromate le json, et envoie le message a l'utilisateur"""
		
		from commons.session import Session
		
		sender = Session().get(sender)
		receiver =  Session().get(to)
		json = Protocol.forgeJSON('message', '["' + sender.getName() + '", "' + message + '"]',
											  {'channel': channelName, 'app': appName})
		receiver.addResponse(json)