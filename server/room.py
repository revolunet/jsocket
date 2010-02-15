##
# room.py
##

from channel import Channel
from log import Log

def addslashes(str):
	return str.replace('"', '$$')

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
		
		if channelName and self.__channelExists(channelName):
			return self.rooms[channelName].list_users()
		else:
			users = []
			for room in self.rooms:
				users.append(self.rooms[room].list_users())
			return users
	
	def create(self, args):
		"""Return Ajoute un channel a la liste des rooms  -> bool"""
		
		if self.__channelExists(args[0]) == False:
			self.rooms[args[0]] = Channel(args[0])
			if args[1]:
				self.rooms[args[0]].channelPwd = args[1]
			return True
		return False
		
	def remove(self, channelName):
		"""Return : Supprime un channel de la liste des rooms -> bool """
		
		if self.__channelExists(channelName):
			self.rooms.pop(channelName)
			return True
		return False
		
	def join(self, args, client):
		"""Return Ajoute un utilisateur dans la room specifie  -> bool """
		
		if self.__channelExists(args[0]):
			if self.rooms[args[0]].isProtected() and args[1]:
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
		
		if self.__channelExists(channelName):
			self.rooms[channelName].delete(client)
			self.count_users = self.count_users - 1
			return True
		return False
		
	def channel(self, channelName):
		"""Return : le Channel specifie -> Channel """
		
		if self.__channelExists(channelName):
			return self.rooms[channelName]
		return None
	
	def forward(self, appName, commande):
		"""Return : Envoie une commande a tous les utilisateurs d'un channel -> bool """
		
		if self.__channelExists(appName):
			list_users = self.list_users(appName)
			if len(list_users) >= 1:
				for user in list_users:
					if user.master == False:
						user.queue_cmd('{"from": "forward", "value": ["' + self.channel(appName).get_master().get_name() + '", "' + addslashes(commande) + '"], "app" : "' + appName + '"}')
				return True
		return False
		
	def message(self, appName, sender, users, message):
		"""Return : Envoie un message a une liste d'utilisateurs -> bool """
		
		if self.__channelExists(appName):
			if sender in self.channel(appName).list_users():
				master = self.channel(appName).get_master()
				if len(users) > 0:
					list_users = self.list_users(appName)
					if users[0] == 'master' and master:
						master.queue_cmd('{"from": "message", "value": ["' + sender.get_name() + '", "' + message + '"], "app" : "' + appName + '"}')
						return True
					elif users[0] == 'all':
						if len(list_users) >= 1:
							for user in list_users:
								user.queue_cmd('{"from": "message", "value": ["' + sender.get_name() + '", "' + message + '"], "app" : "' + appName + '"}')
							return True
						return False
					else:
						if len(list_users) >= 1:
							for user in list_users:
								if user.get_name() in users:
									user.queue_cmd('{"from": "message", "value": ["' + sender.get_name() + '", "' + message + '"], "app" : "' + appName + '"}')
							return True
						return False
		return False
	
	def chanAuth(self, appName, adminPwd, client):
		if self.__channelExists(appName):
			return self.channel(appName).auth(adminPwd, client)
		return False
		
	def total_users(self):
		"""Return : le nombre d'utilisateurs connectes -> int """
		
		return self.count_users
		
	def __channelExists(self, channelName):
		"""Return : si le channel existe ou non -> bool """
		
		return channelName in self.rooms