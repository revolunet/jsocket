##
# Protocol.py
##


import simplejson
from log.logger import Log


def isMaster(attrs):
	def _isMaster(f):
		def decorated(self, *args, **kwargs):
			if self.client.master:
				return f(self, *args, **kwargs)
			self.client.sput('{"from": "'+attrs+'", "value": false, "message": "Vous n%22etes pas administrateur du serveur."}')
			return False
		return decorated
	return _isMaster

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
						if json_cmd.get('uid', None) is not None:
							self.client.unique_key = json_cmd.get('uid')
						if json_cmd.get('app', None) == None or len(json_cmd.get('app', None)) == 0:
							json_cmd['app'] = "null"
						if json_cmd.get('channel', None) == None or len(json_cmd.get('channel', None)) == 0:
							json_cmd['channel'] = "null"
						if json_cmd.get('args', None) is not None and json_cmd.get('channel', None) is not None and json_cmd.get('app', None) is not None:
							arg = {'channel' : json_cmd['channel'], 'app' : json_cmd['app'], 'uid': self.client.unique_key, 'data': json_cmd['args']}
							self.__cmd_list [json_cmd['cmd']](arg)
							#self.__cmd_list [json_cmd['cmd']](json_cmd['args'], , json_cmd['app'])
							self.client.validJson = True
						else:
							Log().add("[+] Command error : " + cmd + " , '" + json_cmd['cmd'] + "' arguments invalides", 'ired')
							self.client.validJson = False
					except KeyError as e:
						Log().add("[+] Command error : " + cmd + " , '" + json_cmd['cmd'] + "' prends deux arguments", 'ired')
						self.client.validJson = False
				else:
					Log().add("[+] Command error : " + cmd + " , '" + json_cmd['cmd'] + "' n'est pas une commande valide", 'yellow')
					self.client.validJson = False
			except ValueError:
				Log().add("[+] Command error : " + cmd + " , n'est pas une chaine json valide", 'ired')
				self.client.validJson = False
	
	# {"cmd" : "connected", "args": "null"}
	def __cmd_connected(self, args = None):
		"""Le client est connecte, sa cle unique lui est send"""
		
		self.client.sput('{"from": "connected", "value": "' + str(self.client.unique_key) + '"}')

	# {"cmd" : "auth", "args": "masterpassword", "channel": "", "app" : ""}
	def __cmd_auth(self, args):
		"""
		Authentifie un client en tant que master du server.
		"""
		
		if args['data'] == self.client.master_password:
			self.client.master = True
			Log().add("[+] Client : le client " + str(self.client.client_address) + " est a present master du serveur")
			self.client.sput('{"from": "auth", "value": true, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
		else:
			self.client.sput('{"from": "auth", "value": false, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')

	# {"cmd": "list", "args": "channelName", "channel": "", "app" : ""}
	def __cmd_list(self, args):
		""" Retourne la liste d'utilisateurs d'un channel """
		
		str = [ ]
		if args['channel'] is None:
			users = self.client.room.list_users(args)
		else:
			users = self.client.room.list_users(args['channel'])
		for user in users:
			status = user.status
			key = user.unique_key
			name = user.get_name()
			to_send = {"name": name, "key": key, "status": status}
			str.append(to_send)
		self.client.sput('{"from": "list", "value": ' + simplejson.JSONEncoder().encode(str) + ', "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')

	# flash-player send <policy-file-request/>
	def __cmd_policy(self):
		"""
		Retourne la policy pour un client flash.
		"""
		
		Log().add("[+] Send policy file request to " + str(self.client.client_address))
		self.client.sput("<cross-domain-policy><allow-access-from domain='*' to-ports='*' secure='false' /></cross-domain-policy>")

	# {"cmd": "delete", "args": "irc", "channel": "", "app" : ""}
	@isMaster('remove')
	def __cmd_remove(self, args):
		"""On supprimet un channel, si celui si existe et que Client est Master"""
		
		if self.client.room.remove(args['data']):
			self.client.sput('{"from": "remove", "value": true, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
			Log().add("[+] Le channel " + args['data'] + " a ete supprime par : " + str(self.client.client_address))
		else:
			Log().add("[+] Command error : la commande delete a echoue ( le channel " + args['data'] + " n'existe pas )", 'yellow')
			self.client.sput('{"from": "remove", "value": false, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
			
	# {"cmd": "create", "args": ["irc", "appPwd"], "channel": "", "app" : ""}
	@isMaster('create')
	def __cmd_create(self, args):
		"""Creation d'un nouveau channel si le Client est Master"""
		
		if self.client.room.create(args['data'], self.client):
			Log().add("[+] Un nouveau channel a ete ajoute par : " + str(self.client.client_address))
			self.client.sput('{"from": "create", "value": "'+str(self.client.room.channel(args['data'][0]).masterPwd)+'", "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
		else:
			Log().add("[+] Command error : la commande create a echoue ( le channel existe deja )", 'yellow')
			self.client.sput('{"from": "create", "value": false, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')

	# {"cmd": "join", "args": ["irc", ""]}
	def __cmd_join(self, args):
		"""Ajoute un client dans le salon specifie"""
		
		if self.client.room.join(args['data'], self.client):
			self.client.room_name = args['data'][0]
			Log().add("[+] Client : l'utilisateur " + str(self.client.client_address) + " a rejoin le channel : " + args['data'][0], 'yellow')
			self.client.sput('{"from": "join", "value": true, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
			if self.client.master == False:
				self.status(self.client)
			else:
				self.status(self.client, True)
		else:
			Log().add("[+] Command error : le channel " + args['data'][0] + " n'existe pas ", 'yellow')
			self.client.sput('{"from": "join", "value": false, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
	
	# {"cmd": "part", "args": "irc"}
	def __cmd_part(self, args):
		"""Supprime un client du salon specifie"""
		
		if self.client.room_name and self.client.room.part(args, self.client):
			self.client.room_name = None
			self.client.status = "offline"
			Log().add("[+] Client : le client " + str(self.client.client_address) + " a quitte le channel : " + args['data'])
			self.client.sput('{"from": "part", "value": true, "channel": "'+args['data']+'", "app": "'+args['app']+'"}')
			if self.client.master == False:
				self.status(self.client)
		else:
			Log().add("Command error : l'utilisateur n'est pas dans le channel : " + args['data'])
			self.client.sput('{"from": "part", "value": false, "channel": "'+args['data']+'", "app": "'+args['app']+'"}')
	
	# {"cmd": "chanAuth", "args": "passphrase", "channel": "channelName", "app" : ""}
	def __cmd_chanAuth(self, args):
		"""Auth pour definir si le Client est desormais master ou non d'une application"""
		
		if self.client.room.chanAuth(args['channel'], args['data'], self.client):
			Log().add("[+] Client : le client " + str(self.client.client_address) + " est a present master du channel : " + args['channel'])
			self.client.sput('{"from": "chanAuth", "value": true, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
		else:
			self.client.sput('{"from": "chanAuth", "value": false, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
	
	# {"cmd": "forward", "args": "message", "channel": "channelName", "app" : ""}
	@isMaster('forward')
	def __cmd_forward(self, args):
		"""Envoie une commande a tous les clients presents dans le channel"""
		
		if args['channel'] and args['app'] and self.client.room.forward(args['channel'], args['data'], self.client, args['app']):
			Log().add("[+] La commande : "+ args['data'] + " a ete envoye a tous les utilisateurs du channel : " + str(args['channel']))
			self.client.sput('{"from": "forward", "value": true, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
		else:
			if self.client.room_name is None:
				Log().add("[+] Command error : la commande forward a echoue ( le Client n'est dans aucun channel )", 'yellow')
			else:
				Log().add("[+] Command error : la commande forward a echoue ( Aucun autre client dans le salon )", 'yellow')
			self.client.sput('{"from": "forward", "value": false, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
			
	# {"cmd": "message", "args": ['mon message', ['*']], "channel": "channelName", "app" : "" }
	def __cmd_message(self, args):
		"""Envoie un message a une liste d'utilisateurs"""
		
		message = args['data']
		if len(message) == 0:
			self.client.sput('{"from": "message", "value": false, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
		else:
			ret = False
			if len(message[0]) != 0:
				if len(message[1]) > 0:
					if len(message[1][0]) == 0:
						ret = self.client.room.message(args['channel'], self.client, ['master'], message[0], args['app'])
					elif message[1][0] == '*':
						ret = self.client.room.message(args['channel'], self.client, ['all'], message[0], args['app'])
					elif message[1][0] == 'master':
						ret = self.client.room.message(args['channel'], self.client, ['master'], message[0], args['app'])
					else:
						ret = self.client.room.message(args['channel'], self.client, message[1], message[0], args['app'])
				else:
					ret = self.client.room.message(args['channel'], self.client, ['master'], message[0], args['app'])
			if ret:
				self.client.sput('{"from": "message", "value": true, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')	
			else:
				self.client.sput('{"from": "message", "value": false, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
	
	# {"cmd": "nick", "args": "nickName", "app": "appName"}
	def __cmd_nick(self, args):
		"""Permet au client de change de pseudo"""
		
		Log().add("[+] Client : le client " + str(self.client.get_name()) + " a change son nickname en : " + args['data'])
		self.client.nickName = args['data']
		self.client.sput('{"from": "nick", "value": true, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
	
	# {"cmd": "getStatus", "args": "null"}
	def __cmd_getStatus(self, args):
		"""Retourne le status de l'utilisateur"""
		
		Log().add("[+] Client : le client " + str(self.client.get_name()) + " a demande son status")
		self.client.sput('{"from": "getStatus", "value": "' + self.client.status + '", "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
		
	# {"cmd": "setStatus", "args": "newStatus"}
	def __cmd_setStatus(self, args):
		"""Change le status de l'utilisateur"""
		
		Log().add("[+] Client : le client " + str(self.client.get_name()) + " a change son status en : " + args)
		self.client.status = args['data']
		self.client.sput('{"from": "setStatus", "value": true, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')

	# {"cmd": "timeConnect", "args": "null"}
	def __cmd_timeConnect(self, args):
		"""Retourne l'heure a laquelle c'est connecte le client"""
		
		Log().add("[+] Client : le client " + str(self.client.get_name()) + " a demande l'heure de connection")
		self.client.sput('{"from": "timeConnect", "value": "' + self.client.connection_time + '", "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
	
	# {"cmd": "chanMasterPwd", "args": "NEWPASSWORD", "channel": "channelName", "app" : ""}
	def __cmd_chanMasterPwd(self, args):
		"""Change le mot de passe master d'un channel"""
		
		if self.client.master and self.client.room.changeChanMasterPwd(args, args['channel']):
			Log().add("[+] Client : le client " + str(self.client.get_name()) + " a changer le mot de passe master du channel : " + args['app'])
			self.client.sput('{"from": "chanMasterPwd", "value": true, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
		else:
			if self.client.master == False:
				Log().add("[+] Command error : la commande chanMasterPwd a echoue ( le Client n'est pas master )", 'yellow')
			elif self.client.room.channelExists(args[0]) == False:
				Log().add("[+] Command error : la commande chanMasterPwd a echoue ( le channel n'existe pas )", 'yellow')	
			else:
				Log().add("[+] Command error : la commande chanMasterPwd a echoue", 'yellow')
			self.client.sput('{"from": "chanMasterPwd", "value": false, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
		
	def status(self, client, master = False):
		"""
		Envoie le status aux clients lors d'une action ( join / part ... connect ...)
		"""
		
		if client.room_name:
			channel = client.room.channel(client.room_name)
			if channel and master == False:
				master = channel.get_master()
				if master:
					if client.room_name:
						channel = client.room_name
					else:
						channel = "none"
					status = client.status
					key = client.unique_key
					name = client.get_name()
					to_send = {"name": name, "key": key, "status": status}
					Log().add("[+] Client : envoie du status de " + name + " vers l'utilisateur : " + master.get_name())
					master.queue_cmd('{"from": "status", "value": '+ simplejson.JSONEncoder().encode(to_send) +', "channel": "'+channel+'"}')
			else:
				for user in channel.client_list:
					if user.master != client:
						status = client.status
						key = client.unique_key
						name = client.get_name()
						to_send = {"name": name, "key": key, "status": status}
						Log().add("[+] Client : envoie du status master vers l'utilisateur : " + name)
						user.queue_cmd('{"from": "status", "value": '+ simplejson.JSONEncoder().encode(to_send) +', "channel": "'+client.room_name+'"}')