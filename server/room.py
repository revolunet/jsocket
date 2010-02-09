##
# room.py
##

from channel import Channel

class Room():
	"""docstring for Room"""
	def __init__(self):
		self.rooms = {}
		self.count_users = 0
		self.init_rooms()
		
	def init_rooms(self):
		self.rooms['irc'] = Channel('irc')
		self.rooms['tcp'] = Channel('tcp')
		
	def list_users(self, channelName):
		"""Return : la liste de tous les utilisateurs de la room -> list(Client) """
		
		return self.rooms[channelName].list_users()
	
	def list_users(self):
		"""Return : la liste de tous les utilisateurs du serveur -> list(Client) """
		
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
		
	def total_users(self):
		"""Return : le nombre d'utilisateurs connectes -> int """
		
		return self.count_users
		
	def __channelExists(self, channelName):
		"""Return : si le channel existe ou non -> bool """
		
		return channelName in self.rooms