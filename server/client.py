##
# client.py
##

import threading
import json
import random
from json import JSONEncoder
from log import Log
from settings import *

class Client(threading.Thread):
	def __init__(self, client_socket, client_address, room, rqueue, squeue):
		self.client_socket = client_socket
		self.client_address = client_address
		self.master = False
		self.__nickName = None
		self.__room = room
		self.__master_password = SETTINGS.MASTER_PASSWORD
		self.__init_cmd()
		self.__unique_key = hex(random.getrandbits(64))
		self.__rqueue = rqueue
		self.__squeue = squeue
		self.__room_name = None
		threading.Thread.__init__(self)
		
	def __init_cmd(self):
		"""On initialise la liste des commandes disponnible"""

		self.__cmd_list = {
			'auth' : self.__cmd_auth,
			'create' : self.__cmd_create,
			'join' : self.__cmd_join,
			'part' : self.__cmd_part,
			'chanAuth' : self.__cmd_chanAuth,
			'connected' : self.__cmd_connected,
			'forward' : self.__cmd_forward,
			'policy-file-request' : self.__cmd_policy,
			'remove' : self.__cmd_remove,
			'message' : self.__cmd_message,
			'list' : self.__cmd_list,
			'nick' : self.__cmd_nick
		}
		
	def run(self):
		"""Boucle de lecture du client"""

		while 1:
			data = self.client_socket.recv(1024).strip()
			if len(data) == 0:
				self.__disconnection()
				return
			else:
				self.__rqueue.put([self, data])
				Log().add("[+] Client " + str(self.client_address) + " send : " + data)

	def get_name(self):
		if self.__nickName == None:
			return self.__unique_key
		return self.__nickName

	def parse(self, cmd):
		"""Parsing de l'entre json sur le serveur"""

		if 'policy-file-request' in cmd:
			self.__cmd_list['policy-file-request']()
		else:
			try:
				json_cmd = json.loads(cmd)
				if json_cmd['cmd'] and json_cmd['cmd'] in self.__cmd_list:
					try :
						if json_cmd.get('app', None) == None:
							json_cmd['app'] = "None"
						if json_cmd['args'] and json_cmd['app']:
							self.__cmd_list [json_cmd['cmd']](json_cmd['args'], json_cmd['app'])
					except KeyError:
						Log().add("[+] Command error : " + cmd + " , '" + json_cmd['cmd'] + "' prends deux arguments", 'ired')
				else:
					Log().add("[+] Command error : " + cmd + " , '" + json_cmd['cmd'] + "' n'est pas une commande valide", 'yellow')
			except ValueError:
				Log().add("[+] Command error : " + cmd + " , n'est pas une chaine json valide", 'ired')

	# {"cmd" : "connected", "args": "null"}
	def __cmd_connected(self, args = None, app = None):
		"""Le client est connecte, sa cle unique lui est send"""
		
		self.__squeue.put([self, '{"from": "connected", "value": "' + str(self.__unique_key) + '"}'])

	# {"cmd" : "auth", "args": "masterpassword", "app" : ""}
	def __cmd_auth(self, args, app = None):
		
		if args == self.__master_password:
			self.master = True
			Log().add("[+] Client : le client " + str(self.client_address) + " est a present master du serveur")
			self.__squeue.put([self, '{"from": "auth", "value": true}'])
		else:
			self.__squeue.put([self, '{"from": "auth", "value": false}'])

	# {"cmd": "list", "args": "appName", "app": "appName"}
	def __cmd_list(self, args, app = None):
		""" Retourne la liste d'utilisateurs d'un channel """
		
		users = self.__room.list_users(args)
		str = [ ]
		for user in users:
			str.append(user.get_name())
		self.__squeue.put([self, '{"from": "list", "value": ' + JSONEncoder().encode(str) + '}'])

	# flash-player send <policy-file-request/>
	def __cmd_policy(self):
		self.__squeue.put([self, "<cross-domain-policy><allow-access-from domain='*' to-ports='*' secure='false' /></cross-domain-policy>\0"])

	# {"cmd": "delete", "args": "irc"}
	def __cmd_remove(self, args, app = None):
		"""On supprimet un channel, si celui si existe et que Client est Master"""
		
		if self.master and self.__room.remove(args):
			self.__squeue.put([self, '{"from": "remove", "value": true}'])
			Log().add("[+] Le channel " + args + " a ete supprime par : " + str(self.client_address))
		else:
			if self.master:
				Log().add("[+] Command error : la commande delete a echoue ( le channel " + args + " n'existe pas )", 'yellow')
			else:
				Log().add("[+] Command error : la commande delete a echoue ( le Client n'est pas master )", 'yellow')
			self.__squeue.put([self, '{"from": "remove", "value": false}'])
			
	# {"cmd": "create", "args": ["irc", "appPwd"]}
	def __cmd_create(self, args, app = None):
		"""Creation d'un nouveau channel si le Client est Master"""
		
		if self.master and self.__room.create(args):
			Log().add("[+] Un nouveau channel a ete ajoute par : " + str(self.client_address))
			self.__squeue.put([self, '{"from": "create", "value": true, "app": "'+args[0]+'"}'])
		else:
			if self.master:
				Log().add("[+] Command error : la commande create a echoue ( le channel existe deja )", 'yellow')
			else:
				Log().add("[+] Command error : la commande create a echoue ( le Client n'est pas master )", 'yellow')
			self.__squeue.put([self, '{"from": "create", "value": false}'])

	# {"cmd": "join", "args": ["irc", ""]}
	def __cmd_join(self, args, app = None):
		"""Ajoute un client dans le salon specifie"""
		
		if self.__room.join(args, self):
			self.__room_name = args[0]
			Log().add("[+] Client : l'utilisateur " + str(self.client_address) + " a rejoin le channel : " + args[0], 'yellow')
			self.__squeue.put([self, '{"from": "join", "value": true, "app": "'+args[0]+'"}'])
		else:
			Log().add("[+] Command error : le channel " + args[0] + " n'existe pas ", 'yellow')
			self.__squeue.put([self, '{"from": "join", "value": false, "app": "'+args[0]+'"}'])
			
	
	# {"cmd": "part", "args": "irc"}
	def __cmd_part(self, args, app = None):
		"""Supprime un client du salon specifie"""
		
		if self.__room_name and self.__room.part(self.__room_name, self):
			self.__room_name = None
			Log().add("[+] Client : le client " + str(self.client_address) + " a quitte le channel : " + args)
			self.__squeue.put([self, '{"from": "part", "value": true, "app": "'+args+'"}'])
		else:
			Log().add("Command error : l'utilisateur n'est pas dans le channel : " + args)
			self.__squeue.put([self, '{"from": "part", "value": false, "app": "'+args+'}'])
	
	# {"cmd": "chanAuth", "args": "passphrase", "app" : "irc"}
	def __cmd_chanAuth(self, args, app):
		"""Auth pour definir si le Client est desormais master ou non d'une application"""
		
		if self.__room.chanAuth(app, args, self):
			Log().add("[+] Client : le client " + str(self.client_address) + " est a present master du channel : " + app)
			self.__squeue.put([self, '{"from": "chanAuth", "value": true, "app" : "'+app+'"}'])
		else:
			self.__squeue.put([self, '{"from": "chanAuth", "value": false, "app" : "'+app+'"}'])
	
	# {"cmd": "forward", "args": "message", "app": "irc"}
	def __cmd_forward(self, args, app = None):
		"""Envoie une commande a tous les clients presents dans le channel"""
		
		if app and self.__room.forward(app, args, self):
			Log().add("[+] La commande : "+ args + " a ete envoye a tous les utilisateurs du channel : " + str(app))
			self.__squeue.put([self, '{"from": "forward", "value": true, "app": "'+app+'"}'])
		else:
			if self.master == False:
				Log().add("[+] Command error : la commande forward a echoue ( le Client n'est pas master )", 'yellow')
			elif self.__room_name is None:
				Log().add("[+] Command error : la commande forward a echoue ( le Client n'est dans aucun channel )", 'yellow')
			else:
				Log().add("[+] Command error : la commande forward a echoue ( Aucun autre client dans le salon )", 'yellow')
			self.__squeue.put([self, '{"from": "forward", "value": false, "app": "'+app+'"}'])
			
	def queue_cmd(self, command):
		"""Ajoute une commande a la Queue en cours"""
		
		self.__squeue.put([self, command])
		
	# {"cmd": "message", "args": "['mon message', ['*']]"}
	def __cmd_message(self, message, app):
		"""Envoie un message a une liste d'utilisateurs"""
		
		if len(message) == 0:
			self.__squeue.put([self, '{"from": "message", "value": false, "app" : "'+app+'"}'])
		else:
			ret = False
			if len(message[0]) != 0:
				if len(message[1]) > 0:
					if len(message[1][0]) == 0:
						ret = self.__room.message(app, self, ['master'], message[0])
					elif message[1][0] == '*':
						ret = self.__room.message(app, self, ['all'], message[0])
					elif message[1][0] == 'master':
						ret = self.__room.message(app, self, ['master'], message[0])
					else:
						ret = self.__room.message(app, self, message[1], message[0])
				else:
					ret = self.__room.message(app, self, ['master'], message[0])
			if ret:
				self.__squeue.put([self, '{"from": "message", "value": true, "app" : "'+app+'"}'])	
			else:
				self.__squeue.put([self, '{"from": "message", "value": false, "app" : "'+app+'"}'])
	
	# {"cmd": "nick", "args": "nickName", "app": "appName"}
	def __cmd_nick(self, args, app = None):
		"""Permet au client de change de pseudo"""
		
		Log().add("[+] Client : le client " + str(self.get_name()) + " a change son nickname en : " + args)
		self.__nickName = args
		self.__squeue.put([self, '{"from": "nick", "value": true}'])
				
	def __disconnection(self):
		"""On ferme la socket serveur du client lorsque celui-ci a ferme sa socket cliente"""

		if self.__room_name:
			self.__room.part(self.__room_name, self)			
		self.client_socket.close()
		Log().add("[-] Client disconnected", 'blue')
