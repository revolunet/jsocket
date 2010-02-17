##
# Protocol.py
##

import json
from json import JSONEncoder
from log import Log

class Protocol(object):
	"""docstring for Protocol"""
	def __init__(self, client):
		self.client = client
		self.__init_cmd()
		
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
			'nick' : self.__cmd_nick,
			'getStatus' : self.__cmd_getStatus,
			'setStatus' : self.__cmd_setStatus,
			'timeConnect' : self.__cmd_timeConnect,
			'chanMasterPwd' : self.__cmd_chanMasterPwd
		}
		
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
		
		self.client.squeue.put([self, '{"from": "connected", "value": "' + str(self.client.unique_key) + '"}'])

	# {"cmd" : "auth", "args": "masterpassword", "app" : ""}
	def __cmd_auth(self, args, app = None):
		
		if args == self.client.master_password:
			self.client.master = True
			Log().add("[+] Client : le client " + str(self.client.client_address) + " est a present master du serveur")
			self.client.squeue.put([self, '{"from": "auth", "value": true}'])
		else:
			self.client.squeue.put([self, '{"from": "auth", "value": false}'])

	# {"cmd": "list", "args": "appName", "app": "appName"}
	def __cmd_list(self, args, app = None):
		""" Retourne la liste d'utilisateurs d'un channel """
		
		users = self.client.room.list_users(args)
		str = [ ]
		for user in users:
			str.append(user.get_name())
		self.client.squeue.put([self, '{"from": "list", "value": ' + JSONEncoder().encode(str) + '}'])

	# flash-player send <policy-file-request/>
	def __cmd_policy(self):
		self.client.squeue.put([self, "<cross-domain-policy><allow-access-from domain='*' to-ports='*' secure='false' /></cross-domain-policy>\0"])

	# {"cmd": "delete", "args": "irc"}
	def __cmd_remove(self, args, app = None):
		"""On supprimet un channel, si celui si existe et que Client est Master"""
		
		if self.client.master and self.client.room.remove(args):
			self.client.squeue.put([self, '{"from": "remove", "value": true}'])
			Log().add("[+] Le channel " + args + " a ete supprime par : " + str(self.client.client_address))
		else:
			if self.client.master:
				Log().add("[+] Command error : la commande delete a echoue ( le channel " + args + " n'existe pas )", 'yellow')
			else:
				Log().add("[+] Command error : la commande delete a echoue ( le Client n'est pas master )", 'yellow')
			self.client.squeue.put([self, '{"from": "remove", "value": false}'])
			
	# {"cmd": "create", "args": ["irc", "appPwd"]}
	def __cmd_create(self, args, app = None):
		"""Creation d'un nouveau channel si le Client est Master"""
		
		if self.client.master and self.client.room.create(args, self.client):
			Log().add("[+] Un nouveau channel a ete ajoute par : " + str(self.client.client_address))
			self.client.squeue.put([self, '{"from": "create", "value": "'+str(self.client.room.channel(args[0]).masterPwd)+'", "app": "'+args[0]+'"}'])
		else:
			if self.client.master:
				Log().add("[+] Command error : la commande create a echoue ( le channel existe deja )", 'yellow')
			else:
				Log().add("[+] Command error : la commande create a echoue ( le Client n'est pas master )", 'yellow')
			self.client.squeue.put([self, '{"from": "create", "value": false}'])

	# {"cmd": "join", "args": ["irc", ""]}
	def __cmd_join(self, args, app = None):
		"""Ajoute un client dans le salon specifie"""
		
		if self.client.room.join(args, self.client):
			self.client.room_name = args[0]
			Log().add("[+] Client : l'utilisateur " + str(self.client.client_address) + " a rejoin le channel : " + args[0], 'yellow')
			self.client.squeue.put([self, '{"from": "join", "value": true, "app": "'+args[0]+'"}'])
			if self.client.master == False:
				self.__status(self.client)
		else:
			Log().add("[+] Command error : le channel " + args[0] + " n'existe pas ", 'yellow')
			self.client.squeue.put([self, '{"from": "join", "value": false, "app": "'+args[0]+'"}'])
			
	
	# {"cmd": "part", "args": "irc"}
	def __cmd_part(self, args, app = None):
		"""Supprime un client du salon specifie"""
		
		if self.client.room_name and self.client.room.part(self.client.room_name, self.client):
			self.client.room_name = None
			self.client.status = "offline"
			Log().add("[+] Client : le client " + str(self.client.client_address) + " a quitte le channel : " + args)
			self.client.squeue.put([self, '{"from": "part", "value": true, "app": "'+args+'"}'])
			if self.client.master == False:
				self.__status(self.client)
		else:
			Log().add("Command error : l'utilisateur n'est pas dans le channel : " + args)
			self.client.squeue.put([self, '{"from": "part", "value": false, "app": "'+args+'}'])
	
	# {"cmd": "chanAuth", "args": "passphrase", "app" : "irc"}
	def __cmd_chanAuth(self, args, app):
		"""Auth pour definir si le Client est desormais master ou non d'une application"""
		
		if self.client.room.chanAuth(app, args, self.client):
			Log().add("[+] Client : le client " + str(self.client.client_address) + " est a present master du channel : " + app)
			self.client.squeue.put([self, '{"from": "chanAuth", "value": true, "app" : "'+app+'"}'])
		else:
			self.client.squeue.put([self, '{"from": "chanAuth", "value": false, "app" : "'+app+'"}'])
	
	# {"cmd": "forward", "args": "message", "app": "irc"}
	def __cmd_forward(self, args, app = None):
		"""Envoie une commande a tous les clients presents dans le channel"""
		
		if app and self.client.room.forward(app, args, self.client):
			Log().add("[+] La commande : "+ args + " a ete envoye a tous les utilisateurs du channel : " + str(app))
			self.client.squeue.put([self, '{"from": "forward", "value": true, "app": "'+app+'"}'])
		else:
			if self.client.master == False:
				Log().add("[+] Command error : la commande forward a echoue ( le Client n'est pas master )", 'yellow')
			elif self.client.room_name is None:
				Log().add("[+] Command error : la commande forward a echoue ( le Client n'est dans aucun channel )", 'yellow')
			else:
				Log().add("[+] Command error : la commande forward a echoue ( Aucun autre client dans le salon )", 'yellow')
			self.client.squeue.put([self, '{"from": "forward", "value": false, "app": "'+app+'"}'])
			
	# {"cmd": "message", "args": ['mon message', ['*']], "app": "" }
	def __cmd_message(self, message, app):
		"""Envoie un message a une liste d'utilisateurs"""
		
		if len(message) == 0:
			self.client.squeue.put([self, '{"from": "message", "value": false, "app" : "'+app+'"}'])
		else:
			ret = False
			if len(message[0]) != 0:
				if len(message[1]) > 0:
					if len(message[1][0]) == 0:
						ret = self.client.room.message(app, self.client, ['master'], message[0])
					elif message[1][0] == '*':
						ret = self.client.room.message(app, self.client, ['all'], message[0])
					elif message[1][0] == 'master':
						ret = self.client.room.message(app, self.client, ['master'], message[0])
					else:
						ret = self.client.room.message(app, self.client, message[1], message[0])
				else:
					ret = self.client.room.message(app, self.client, ['master'], message[0])
			if ret:
				self.client.squeue.put([self, '{"from": "message", "value": true, "app" : "'+app+'"}'])	
			else:
				self.client.squeue.put([self, '{"from": "message", "value": false, "app" : "'+app+'"}'])
	
	# {"cmd": "nick", "args": "nickName", "app": "appName"}
	def __cmd_nick(self, args, app = None):
		"""Permet au client de change de pseudo"""
		
		Log().add("[+] Client : le client " + str(self.client.get_name()) + " a change son nickname en : " + args)
		self.client.nickName = args
		self.client.squeue.put([self, '{"from": "nick", "value": true}'])
	
	# {"cmd": "getStatus", "args": "null"}
	def __cmd_getStatus(self, args, app = None):
		"""Retourne le status de l'utilisateur"""
		
		Log().add("[+] Client : le client " + str(self.client.get_name()) + " a demande son status")
		self.client.squeue.put([self, '{"from": "getStatus", "value": "' + self.client.status + '"}'])
		
	# {"cmd": "setStatus", "args": "newStatus"}
	def __cmd_setStatus(self, args, app = None):
		"""Change le status de l'utilisateur"""
		
		Log().add("[+] Client : le client " + str(self.client.get_name()) + " a change son status en : " + args)
		self.client.status = args
		self.client.squeue.put([self, '{"from": "setStatus", "value": true}'])

	# {"cmd": "timeConnect", "args": "null"}
	def __cmd_timeConnect(self, args, app = None):
		"""Retourne l'heure a laquelle c'est connecte le client"""
		
		Log().add("[+] Client : le client " + str(self.client.get_name()) + " a demande l'heure de connection")
		self.client.squeue.put([self, '{"from": "timeConnect", "value": "' + self.client.connection_time + '"}'])
	
	# {"cmd": "chanMasterPwd", "args": "NEWPASSWORD", "app", "channelName"}
	def __cmd_chanMasterPwd(self, args, app = None):
		"""Change le mot de passe master d'un channel"""
		
		if self.client.master and self.client.room.changeChanMasterPwd(args, app):
			Log().add("[+] Client : le client " + str(self.client.get_name()) + " a changer le mot de passe master du channel : " + app)
			self.client.squeue.put([self, '{"from": "chanMasterPwd", "value": true}'])
		else:
			if self.client.master == False:
				Log().add("[+] Command error : la commande chanMasterPwd a echoue ( le Client n'est pas master )", 'yellow')
			elif self.client.room.channelExists(args[0]) == False:
				Log().add("[+] Command error : la commande chanMasterPwd a echoue ( le channel n'existe pas )", 'yellow')	
			else:
				Log().add("[+] Command error : la commande chanMasterPwd a echoue", 'yellow')
			self.client.squeue.put([self, '{"from": "chanMasterPwd", "value": false}'])
		
	def __status(self, client):
		
		if client.room_name:
			channel = client.room.channel(client.room_name)
			if channel:
				master = channel.get_master()
				if master:
					master.queue_cmd('{"from": "status", "value": ["'+client.get_name()+'", "'+client.status+'"], "app", "'+client.room_name+'"}')
