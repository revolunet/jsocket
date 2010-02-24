##
# Protocol.py
##


import simplejson
from log.logger import Log

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
				json_cmd = simplejson.loads(cmd)
				if json_cmd.get('cmd', None) is not None and json_cmd['cmd'] in self.__cmd_list:
					try :
						if json_cmd.get('app', None) == None or len(json_cmd.get('app', None)) == 0:
							json_cmd['app'] = "null"
						if json_cmd.get('channel', None) == None or len(json_cmd.get('channel', None)) == 0:
							json_cmd['channel'] = "null"
						if json_cmd.get('args', None) is not None and json_cmd.get('channel', None) is not None and json_cmd.get('app', None) is not None:
							self.__cmd_list [json_cmd['cmd']](json_cmd['args'], json_cmd['channel'], json_cmd['app'])
						else:
							Log().add("[+] Command error : " + cmd + " , '" + json_cmd['cmd'] + "' arguments invalides", 'ired')
					except KeyError:
						Log().add("[+] Command error : " + cmd + " , '" + json_cmd['cmd'] + "' prends deux arguments", 'ired')
				else:
					Log().add("[+] Command error : " + cmd + " , '" + json_cmd['cmd'] + "' n'est pas une commande valide", 'yellow')
			except ValueError:
				Log().add("[+] Command error : " + cmd + " , n'est pas une chaine json valide", 'ired')
	
	# {"cmd" : "connected", "args": "null"}
	def __cmd_connected(self, args = None, channel = None, app = None):
		"""Le client est connecte, sa cle unique lui est send"""
		
		self.client.squeue.put([self, '{"from": "connected", "value": "' + str(self.client.unique_key) + '"}'])

	# {"cmd" : "auth", "args": "masterpassword", "channel": "", "app" : ""}
	def __cmd_auth(self, args, channel = None, app = None):
		
		if args == self.client.master_password:
			self.client.master = True
			Log().add("[+] Client : le client " + str(self.client.client_address) + " est a present master du serveur")
			self.client.squeue.put([self, '{"from": "auth", "value": true, "channel": "'+channel+'", "app": "'+app+'"}'])
		else:
			self.client.squeue.put([self, '{"from": "auth", "value": false, "channel": "'+channel+'", "app": "'+app+'"}'])

	# {"cmd": "list", "args": "channelName", "channel": "", "app" : ""}
	def __cmd_list(self, args, channel = None, app = None):
		""" Retourne la liste d'utilisateurs d'un channel """
		
		str = [ ]
		if channel is None:
			users = self.client.room.list_users(args)
		else:
			users = self.client.room.list_users(channel)
		for user in users:
			status = user.status
			key = user.unique_key
			name = user.get_name()
			to_send = {"name": name, "key": key, "status": status}
			str.append(to_send)
		self.client.squeue.put([self, '{"from": "list", "value": ' + simplejson.JSONEncoder().encode(str) + ', "channel": "'+channel+'", "app": "'+app+'"}'])

	# flash-player send <policy-file-request/>
	def __cmd_policy(self):
		Log().add("[+] Send policy file request to " + str(self.client.client_address))
		self.client.squeue.put([self, "<cross-domain-policy><allow-access-from domain='*' to-ports='*' secure='false' /></cross-domain-policy>"])

	# {"cmd": "delete", "args": "irc", "channel": "", "app" : ""}
	def __cmd_remove(self, args, channel = None, app = None):
		"""On supprimet un channel, si celui si existe et que Client est Master"""
		
		if self.client.master and self.client.room.remove(args):
			self.client.squeue.put([self, '{"from": "remove", "value": true, "channel": "'+channel+'", "app": "'+app+'"}'])
			Log().add("[+] Le channel " + args + " a ete supprime par : " + str(self.client.client_address))
		else:
			if self.client.master:
				Log().add("[+] Command error : la commande delete a echoue ( le channel " + args + " n'existe pas )", 'yellow')
			else:
				Log().add("[+] Command error : la commande delete a echoue ( le Client n'est pas master )", 'yellow')
			self.client.squeue.put([self, '{"from": "remove", "value": false, "channel": "'+channel+'", "app": "'+app+'"}'])
			
	# {"cmd": "create", "args": ["irc", "appPwd"], "channel": "", "app" : ""}
	def __cmd_create(self, args, channel = None, app = None):
		"""Creation d'un nouveau channel si le Client est Master"""
		
		if self.client.master and self.client.room.create(args, self.client):
			Log().add("[+] Un nouveau channel a ete ajoute par : " + str(self.client.client_address))
			self.client.squeue.put([self, '{"from": "create", "value": "'+str(self.client.room.channel(args[0]).masterPwd)+'", "channel": "'+channel+'", "app": "'+app+'"}'])
		else:
			if self.client.master:
				Log().add("[+] Command error : la commande create a echoue ( le channel existe deja )", 'yellow')
			else:
				Log().add("[+] Command error : la commande create a echoue ( le Client n'est pas master )", 'yellow')
			self.client.squeue.put([self, '{"from": "create", "value": false, "channel": "'+channel+'", "app": "'+app+'"}'])

	# {"cmd": "join", "args": ["irc", ""]}
	def __cmd_join(self, args, channel = None, app = None):
		"""Ajoute un client dans le salon specifie"""
		
		if self.client.room.join(args, self.client):
			self.client.room_name = args[0]
			Log().add("[+] Client : l'utilisateur " + str(self.client.client_address) + " a rejoin le channel : " + args[0], 'yellow')
			self.client.squeue.put([self, '{"from": "join", "value": true, "channel": "'+channel+'", "app": "'+app+'"}'])
			if self.client.master == False:
				self.status(self.client)
			else:
				self.status(self.client, True)
		else:
			Log().add("[+] Command error : le channel " + args[0] + " n'existe pas ", 'yellow')
			self.client.squeue.put([self, '{"from": "join", "value": false, "channel": "'+channel+'", "app": "'+app+'"}'])
			
	
	# {"cmd": "part", "args": "irc"}
	def __cmd_part(self, args, channel = None, app = None):
		"""Supprime un client du salon specifie"""
		
		if self.client.room_name and self.client.room.part(args, self.client):
			self.client.room_name = None
			self.client.status = "offline"
			Log().add("[+] Client : le client " + str(self.client.client_address) + " a quitte le channel : " + args)
			self.client.squeue.put([self, '{"from": "part", "value": true, "channel": "'+args+'", "app": "'+app+'"}'])
			if self.client.master == False:
				self.status(self.client)
		else:
			Log().add("Command error : l'utilisateur n'est pas dans le channel : " + args)
			self.client.squeue.put([self, '{"from": "part", "value": false, "channel": "'+args+'", "app": "'+app+'"}'])
	
	# {"cmd": "chanAuth", "args": "passphrase", "channel": "channelName", "app" : ""}
	def __cmd_chanAuth(self, args, channel = None, app = None):
		"""Auth pour definir si le Client est desormais master ou non d'une application"""
		
		if self.client.room.chanAuth(channel, args, self.client):
			Log().add("[+] Client : le client " + str(self.client.client_address) + " est a present master du channel : " + channel)
			self.client.squeue.put([self, '{"from": "chanAuth", "value": true, "channel": "'+channel+'", "app": "'+app+'"}'])
		else:
			self.client.squeue.put([self, '{"from": "chanAuth", "value": false, "channel": "'+channel+'", "app": "'+app+'"}'])
	
	# {"cmd": "forward", "args": "message", "channel": "channelName", "app" : ""}
	def __cmd_forward(self, args, channel = None, app = None):
		"""Envoie une commande a tous les clients presents dans le channel"""
		
		if channel and app and self.client.room.forward(channel, args, self.client, app):
			Log().add("[+] La commande : "+ args + " a ete envoye a tous les utilisateurs du channel : " + str(channel))
			self.client.squeue.put([self, '{"from": "forward", "value": true, "channel": "'+channel+'", "app": "'+app+'"}'])
		else:
			if self.client.master == False:
				Log().add("[+] Command error : la commande forward a echoue ( le Client n'est pas master )", 'yellow')
			elif self.client.room_name is None:
				Log().add("[+] Command error : la commande forward a echoue ( le Client n'est dans aucun channel )", 'yellow')
			else:
				Log().add("[+] Command error : la commande forward a echoue ( Aucun autre client dans le salon )", 'yellow')
			self.client.squeue.put([self, '{"from": "forward", "value": false, "channel": "'+channel+'", "app": "'+app+'"}'])
			
	# {"cmd": "message", "args": ['mon message', ['*']], "channel": "channelName", "app" : "" }
	def __cmd_message(self, message, channel = None, app = None):
		"""Envoie un message a une liste d'utilisateurs"""
		
		if len(message) == 0:
			self.client.squeue.put([self, '{"from": "message", "value": false, "channel": "'+channel+'", "app": "'+app+'"}'])
		else:
			ret = False
			if len(message[0]) != 0:
				if len(message[1]) > 0:
					if len(message[1][0]) == 0:
						ret = self.client.room.message(channel, self.client, ['master'], message[0], app)
					elif message[1][0] == '*':
						ret = self.client.room.message(channel, self.client, ['all'], message[0], app)
					elif message[1][0] == 'master':
						ret = self.client.room.message(channel, self.client, ['master'], message[0], app)
					else:
						ret = self.client.room.message(channel, self.client, message[1], message[0], app)
				else:
					ret = self.client.room.message(channel, self.client, ['master'], message[0], app)
			if ret:
				self.client.squeue.put([self, '{"from": "message", "value": true, "channel": "'+channel+'", "app": "'+app+'"}'])	
			else:
				self.client.squeue.put([self, '{"from": "message", "value": false, "channel": "'+channel+'", "app": "'+app+'"}'])
	
	# {"cmd": "nick", "args": "nickName", "app": "appName"}
	def __cmd_nick(self, args, channel = None, app = None):
		"""Permet au client de change de pseudo"""
		
		Log().add("[+] Client : le client " + str(self.client.get_name()) + " a change son nickname en : " + args)
		self.client.nickName = args
		self.client.squeue.put([self, '{"from": "nick", "value": true, "channel": "'+channel+'", "app": "'+app+'"}'])
	
	# {"cmd": "getStatus", "args": "null"}
	def __cmd_getStatus(self, args, channel = None, app = None):
		"""Retourne le status de l'utilisateur"""
		
		Log().add("[+] Client : le client " + str(self.client.get_name()) + " a demande son status")
		self.client.squeue.put([self, '{"from": "getStatus", "value": "' + self.client.status + '", "channel": "'+channel+'", "app": "'+app+'"}'])
		
	# {"cmd": "setStatus", "args": "newStatus"}
	def __cmd_setStatus(self, args, channel = None, app = None):
		"""Change le status de l'utilisateur"""
		
		Log().add("[+] Client : le client " + str(self.client.get_name()) + " a change son status en : " + args)
		self.client.status = args
		self.client.squeue.put([self, '{"from": "setStatus", "value": true, "channel": "'+channel+'", "app": "'+app+'"}'])

	# {"cmd": "timeConnect", "args": "null"}
	def __cmd_timeConnect(self, args, channel = None, app = None):
		"""Retourne l'heure a laquelle c'est connecte le client"""
		
		Log().add("[+] Client : le client " + str(self.client.get_name()) + " a demande l'heure de connection")
		self.client.squeue.put([self, '{"from": "timeConnect", "value": "' + self.client.connection_time + '", "channel": "'+channel+'", "app": "'+app+'"}'])
	
	# {"cmd": "chanMasterPwd", "args": "NEWPASSWORD", "channel": "channelName", "app" : ""}
	def __cmd_chanMasterPwd(self, args, channel = None, app = None):
		"""Change le mot de passe master d'un channel"""
		
		if self.client.master and self.client.room.changeChanMasterPwd(args, channel):
			Log().add("[+] Client : le client " + str(self.client.get_name()) + " a changer le mot de passe master du channel : " + app)
			self.client.squeue.put([self, '{"from": "chanMasterPwd", "value": true, "channel": "'+channel+'", "app": "'+app+'"}'])
		else:
			if self.client.master == False:
				Log().add("[+] Command error : la commande chanMasterPwd a echoue ( le Client n'est pas master )", 'yellow')
			elif self.client.room.channelExists(args[0]) == False:
				Log().add("[+] Command error : la commande chanMasterPwd a echoue ( le channel n'existe pas )", 'yellow')	
			else:
				Log().add("[+] Command error : la commande chanMasterPwd a echoue", 'yellow')
			self.client.squeue.put([self, '{"from": "chanMasterPwd", "value": false, "channel": "'+channel+'", "app": "'+app+'"}'])
		
	def status(self, client, master = False):
		
		if client.room_name:
			channel = client.room.channel(client.room_name)
			if channel and master == False:
				master = channel.get_master()
				if master:
					if client.room_name:
						channel = client.room_name
					else:
						channel = "none"
					master.queue_cmd('{"from": "status", "value": ["'+client.get_name()+'", "'+client.status+'"], "channel": "'+channel+'"}')
			else:
				for user in channel.client_list:
					if user.master == False:
						user.queue_cmd('{"from": "status", "value": ["'+client.get_name()+'", "'+client.status+'"], "channel": "'+client.room_name+'"}')