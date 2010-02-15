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
	
	def create(self, channelName):
		"""Return Ajoute un channel a la liste des rooms  -> bool"""
		
		if self.__channelExists(channelName) == False:
			self.rooms[channelName] = Channel(channelName)
			return True
		return False
		
	def remove(self, channelName):
		"""Return : Supprime un channel de la liste des rooms -> bool """
		
		if self.__channelExists(channelName):
			self.rooms.pop(channelName)
			return True
		return False
		
	def join(self, channelName, client):
		"""Return Ajoute un utilisateur dans la room specifie  -> bool """
		
		if self.__channelExists(channelName):
			self.rooms[channelName].add(client)
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
	
	def forward(self, channelName, commande):
		"""Return : Envoie une commande a tous les utilisateurs d'un channel -> bool """
		
		if self.__channelExists(channelName):
			list_users = self.list_users(channelName)
			if len(list_users) >= 1:
				for user in list_users:
					if user.master == False:
						user.queue_cmd('{"from": "forward", "value": ["' + self.channel(channelName).get_master().get_name() + '", "' + addslashes(commande) + '"]}')
				return True
		return False
		
	def message(self, channelName, sender, users, message):
		"""Return : Envoie un message a une liste d'utilisateurs -> bool """
		
		if self.__channelExists(channelName):
			master = self.channel(channelName).get_master()
			if len(users) > 0:
				list_users = self.list_users(channelName)
				if users[0] == 'master' and master:
					master.queue_cmd('{"from": "message", "value": ["' + sender + '", "' + addslashes(message) + '"]}')
					return True
				elif users[0] == 'all':
					if len(list_users) >= 1:
						for user in list_users:
							user.queue_cmd('{"from": "message", "value": ["' + sender + '", "' + addslashes(message) + '"]}')
						return True
					return False
				else:
					if len(list_users) >= 1:
						for user in list_users:
							if user.get_name() in users:
								user.queue_cmd('{"from": "message", "value": ["' + sender + '", "' + addslashes(message) + '"]}')
						return True
					return False
		return False
		
	def total_users(self):
		"""Return : le nombre d'utilisateurs connectes -> int """
		
		return self.count_users
		
	def __channelExists(self, channelName):
		"""Return : si le channel existe ou non -> bool """
		
		return channelName in self.rooms