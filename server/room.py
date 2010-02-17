##
# room.py
##

from channel import Channel
from log import Log

class Room():
	"""docstring for Room"""
	def __init__(self):
		self.rooms = {}
		self.count_users = 0
		self.init_rooms()
		
	def init_rooms(self):
		self.rooms['irc'] = Channel('irc')
		self.rooms['tcp'] = Channel('tcp')
	
	def list_users(self, channelName = None):
		"""Return : la liste de tous les utilisateurs du serveur -> list(Client) """
		
		if channelName and self.channelExists(channelName):
			return self.rooms[channelName].list_users()
		else:
			users = []
			for room in self.rooms:
				users.append(self.rooms[room].list_users())
			return users
	
	def create(self, args, master):
		"""Return Ajoute un channel a la liste des rooms  -> bool"""
		
		if self.channelExists(args[0]) == False:
			import random
			self.rooms[args[0]] = Channel(args[0])
			self.rooms[args[0]].masterPwd = random.getrandbits(16)
			self.rooms[args[0]].master = master
			if len(args) > 1:
				self.rooms[args[0]].channelPwd = args[1]
			return True
		return False
		
	def remove(self, channelName):
		"""Return : Supprime un channel de la liste des rooms -> bool """
		
		if self.channelExists(channelName):
			self.rooms.pop(channelName)
			return True
		return False
		
	def join(self, args, client):
		"""Return Ajoute un utilisateur dans la room specifie  -> bool """
		
		if self.channelExists(args[0]):
			if self.rooms[args[0]].isProtected() and len(args) > 1:
				if self.rooms[args[0]].channelPwd == args[1]:
					self.rooms[args[0]].add(client)
				else:
					return False
			else:
				self.rooms[args[0]].add(client)
			self.count_users = self.count_users + 1
			return True
		return False
		
	def part(self, channelName, client):
		"""Return Supprime un utilisateur d'une room  -> bool """
		
		if self.channelExists(channelName):
			self.rooms[channelName].delete(client)
			self.count_users = self.count_users - 1
			return True
		return False
		
	def channel(self, channelName):
		"""Return : le Channel specifie -> Channel """
		
		if self.channelExists(channelName):
			return self.rooms[channelName]
		return None
	
	def forward(self, channelName, commande, client, appName):
		"""Return : Envoie une commande a tous les utilisateurs d'un channel -> bool """
		
		if self.channelExists(channelName):
			if client.master or client == self.channel(channelName).get_master():
				master = (client.master and client or self.channel(channelName).get_master())
				list_users = self.list_users(channelName)
				if len(list_users) >= 1:
					for user in list_users:
						if user.master == False:
							user.queue_cmd('{"from": "forward", "value": ["' + master.get_name() + '", "' + commande + '"], "channel" : "' + channelName + '", "app" : "' + appName + '"}')
					return True
		return False
		
	def message(self, channelName, sender, users, message, appName):
		"""Return : Envoie un message a une liste d'utilisateurs -> bool """

		if self.channelExists(channelName):
			if sender in self.channel(channelName).list_users():
				master = self.channel(channelName).get_master()
				if len(users) > 0:
					list_users = self.list_users(channelName)
					if users[0] == 'master' and master:
						master.queue_cmd('{"from": "message", "value": ["' + sender.get_name() + '", "' + message + '"], "channel" : "' + channelName + '", "app" : "' + appName + '"}')
						return True
					elif users[0] == 'all':
						if len(list_users) >= 1:
							for user in list_users:
								user.queue_cmd('{"from": "message", "value": ["' + sender.get_name() + '", "' + message + '"], "channel" : "' + channelName + '", "app" : "' + appName + '"}')
							return True
						return False
					else:
						if len(list_users) >= 1:
							for user in list_users:
								if user.get_name() in users:
									user.queue_cmd('{"from": "message", "value": ["' + sender.get_name() + '", "' + message + '"], "channel" : "' + channelName + '", "app" : "' + appName + '"}')
							return True
						return False
		return False
	
	def chanAuth(self, appName, adminPwd, client):
		"""Return : Auth un utilisateur sur un channel -> bool """
		
		if self.channelExists(appName):
			return self.channel(appName).auth(adminPwd, client)
		return False
		
	def changeChanMasterPwd(self, adminPwd, appName):
		"""Return : change le mot de passe admin d'un channel -> bool """
		
		if self.channelExists(appName):
			self.channel(appName).masterPwd = adminPwd
			return True
		return False

	def total_users(self):
		"""Return : le nombre d'utilisateurs connectes -> int """
		
		return self.count_users
		
	def channelExists(self, channelName):
		"""Return : si le channel existe ou non -> bool """
		
		return channelName in self.rooms