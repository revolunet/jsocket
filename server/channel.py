
##
# channel.py
##

from log import Log

class Channel():
	"""docstring for Channel"""
	def __init__(self, name):
		self.name = name
		self.master = None
		self.masterPwd = None
		self.channelPwd = None
		self.client_list = []
		
	def add(self, client):
		"""Ajoute un client dans la room specifie"""
		
		self.client_list.append(client)
		Log().add("[+] Room : client " + str(client.client_address) + " joined Room " + self.name)
		Log().add("[+] Room : "  + self.name + " " + str(len(self.client_list)) + " users")
	
	def delete(self, client):
		"""Supprime un client de la room specifie"""
		
		if client in self.client_list:
			Log().add("[+] Room : client " + str(client.client_address) + " left Room " + self.name)
			self.client_list.remove(client)
			Log().add("[+] Room : "  + self.name + " " + str(len(self.client_list)) + " users")
			
	def auth(self, masterPwd, client):
		if masterPwd == self.masterPwd:
			self.master = client
			return True
		return False
		
	def isProtected(self):
		return self.channelPwd != None
		
	def list_users(self):
		"""Return : La liste des utilisateurs de la room : -> list(Client)"""
		
		return self.client_list

	def get_master(self):
		""" Retourne le user master du channel """
		
		return self.master