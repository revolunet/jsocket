
##
# channel.py
##

from log import Log

class Channel():
	"""docstring for Channel"""
	def __init__(self, name):
		self.name = name
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
		
	def list_users(self):
		"""Return : La liste des utilisateurs de la room : -> list(Client)"""
		
		return self.client_list

	def get_master(self):
		""" Retourne le user master du channel """
		
		for client in self.client_list:
			if client.master == True:
				return client
		return None