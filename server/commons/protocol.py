import simplejson

def isMaster(attrs):
	def _isMaster(f):
		def decorated(self, *args, **kwargs):
			if self.client.master:
				return f(self, *args, **kwargs)
			return ('{"from": "'+attrs+'", "value": false, "message": "Vous n%22etes pas administrateur du serveur."}')
		return decorated
	return _isMaster

def jsonPrototype(attrs):
	def _jsonPrototype(f):
		def decorated(self, *args, **kwargs):
			res = f(self, *args, **kwargs)
			json = Protocol.forgeJSON(attrs, res, args[0])
			return json
		return decorated
	return _jsonPrototype

class Protocol(object):
	"""docstring for Protocol"""
	def __init__(self):
		from log.logger import Log
		self.client = None
		self.__init_cmd()

	@staticmethod
	def forgeJSON(methodName, value, param):
		json = '{"from": "' + methodName + '"'
		json += ', "value": ' + value
		if param.get('channel', None) is not None:
			json += ', "channel": "' + param['channel'] + '"'
		if param.get('app', None) is not None:
			json += ', "app": "' + param['app'] + '"'
		json += '}'
		return json

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
			'remove' : self.__cmd_remove,
			'message' : self.__cmd_message,
			'list' : self.__cmd_list,
			'nick' : self.__cmd_nick,
			'getStatus' : self.__cmd_getStatus,
			'setStatus' : self.__cmd_setStatus,
			'timeConnect' : self.__cmd_timeConnect,
			'chanMasterPwd' : self.__cmd_chanMasterPwd
		}

	def parse(self, client, json):
		"""Parsing de l'entre json sur le serveur"""

		if self.__cmd_list.get(json['cmd'], None) is not None:
			self.client = client
			return self.__cmd_list[json['cmd']](json)
		return None

	# {"cmd" : "connected", "args": "null"}
	@jsonPrototype('connected')
	def __cmd_connected(self, args = None):
		"""Le client est connecte, sa cle unique lui est send"""

		return ('"' + str(self.client.unique_key) + '"')

	# {"cmd" : "auth", "args": "masterpassword", "channel": "", "app" : ""}
	@jsonPrototype('auth')
	def __cmd_auth(self, args):
		"""
		Authentifie un client en tant que master du server.
		"""

		from log.logger import Log

		if args['args'] == self.client.master_password:
			self.client.master = True
			Log().add("[+] Client : le client " + str(self.client.getName()) + " est a present master du serveur")
			return ('true')
		return ('false')

	# {"cmd": "list", "args": "channelName", "channel": "", "app" : ""}
	@jsonPrototype('list')
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
			name = user.getName()
			to_send = {"name": name, "key": key, "status": status}
			str.append(to_send)
		return (simplejson.JSONEncoder().encode(str))

	# flash-player send <policy-file-request/>
	def __cmd_policy(self):
		"""
		Retourne la policy pour un client flash.
		"""

		from log.logger import Log

		Log().add("[+] Send policy file request to " + str(self.client.getName()))
		return ("<cross-domain-policy><allow-access-from domain='*' to-ports='*' secure='false' /></cross-domain-policy>")

	# {"cmd": "delete", "args": "irc", "channel": "", "app" : ""}
	@isMaster('remove')
	@jsonPrototype('remove')
	def __cmd_remove(self, args):
		"""On supprimet un channel, si celui si existe et que Client est Master"""

		from log.logger import Log

		if self.client.room.remove(args['args']):
			Log().add("[+] Le channel " + args['args'] + " a ete supprime par : " + str(self.client.getName()))
			return ('true')
		else:
			Log().add("[!] Command error : la commande delete a echoue ( le channel " + args['args'] + " n'existe pas )", 'yellow')
			return ('false')

	# {"cmd": "create", "args": ["irc", "appPwd"], "channel": "", "app" : ""}
	@isMaster('create')
	@jsonPrototype('create')
	def __cmd_create(self, args):
		"""Creation d'un nouveau channel si le Client est Master"""

		from log.logger import Log

		if self.client.room.create(args['args'], self.client):
			Log().add("[+] Un nouveau channel a ete ajoute par : " + str(self.client.getName()))
			return ('"' + str(self.client.room.channel(args['args'][0]).masterPwd) + '"')
		else:
			Log().add("[!] Command error : la commande create a echoue ( le channel existe deja )", 'yellow')
			return ('false')

	# {"cmd": "join", "args": ["irc", ""]}
	@jsonPrototype('join')
	def __cmd_join(self, args):
		"""Ajoute un client dans le salon specifie"""

		from log.logger import Log

		if self.client.room.join(args['args'], self.client):
			self.client.room_name = args['args'][0]
			Log().add("[+] Client : l'utilisateur " + str(self.client.getName()) + " a rejoin le channel : " + args['args'][0], 'yellow')
			if self.client.master == False:
				self.status(self.client)
			else:
				self.status(self.client, True)
			return ('true')
		else:
			Log().add("[!] Command error : le channel " + args['args'][0] + " n'existe pas ", 'yellow')
			return ('false')

	# {"cmd": "part", "args": "irc"}
	@jsonPrototype('part')
	def __cmd_part(self, args):
		"""Supprime un client du salon specifie"""

		from log.logger import Log

		if self.client.room_name and self.client.room.part(args['args'], self.client):
			self.client.room_name = None
			self.client.status = "offline"
			Log().add("[+] Client : le client " + str(self.client.getName()) + " a quitte le channel : " + args['args'])
			if self.client.master == False:
				self.status(self.client)
			return ('true')
		else:
			Log().add("[!] Command error : l'utilisateur n'est pas dans le channel : " + args['args'])
			return ('false')

	# {"cmd": "chanAuth", "args": "passphrase", "channel": "channelName", "app" : ""}
	@jsonPrototype('chanAuth')
	def __cmd_chanAuth(self, args):
		"""Auth pour definir si le Client est desormais master ou non d'une application"""

		from log.logger import Log

		if self.client.room.chanAuth(args['channel'], args['args'], self.client):
			Log().add("[+] Client : le client " + str(self.client.getName()) + " est a present master du channel : " + args['channel'])
			return ('true')
		else:
			return ('false')

	# {"cmd": "forward", "args": "message", "channel": "channelName", "app" : ""}
	@isMaster('forward')
	@jsonPrototype('forward')
	def __cmd_forward(self, args):
		"""Envoie une commande a tous les clients presents dans le channel"""

		from log.logger import Log

		if args['channel'] and args['app'] and self.client.room.forward(args['channel'], args['args'], self.client, args['app']):
			Log().add("[+] La commande : "+ args['args'] + " a ete envoye a tous les utilisateurs du channel : " + str(args['channel']))
			return ('true')
		else:
			if self.client.room_name is None:
				Log().add("[!] Command error : la commande forward a echoue ( le Client n'est dans aucun channel )", 'yellow')
			else:
				Log().add("[!] Command error : la commande forward a echoue ( Aucun autre client dans le salon )", 'yellow')
			return ('false')

	# {"cmd": "message", "args": ['mon message', ['*']], "channel": "channelName", "app" : "" }
	@jsonPrototype('message')
	def __cmd_message(self, args):
		"""Envoie un message a une liste d'utilisateurs"""

		message = args['args']
		if len(message) == 0:
			return ('false')
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
				return ('true')
			else:
				return ('false')

	# {"cmd": "nick", "args": "nickName", "app": "appName"}
	@jsonPrototype('nick')
	def __cmd_nick(self, args):
		"""Permet au client de change de pseudo"""

		from log.logger import Log

		Log().add("[+] Client : le client " + str(self.client.getName()) + " a change son nickname en : " + args['args'])
		self.client.nickName = args['args']
		return ('true')

	# {"cmd": "getStatus", "args": "null"}
	@jsonPrototype('getStatus')
	def __cmd_getStatus(self, args):
		"""Retourne le status de l'utilisateur"""

		from log.logger import Log

		Log().add("[+] Client : le client " + str(self.client.getName()) + " a demande son status")
		return ('"' + self.client.status + '"')

	# {"cmd": "setStatus", "args": "newStatus"}
	@jsonPrototype('setStatus')
	def __cmd_setStatus(self, args):
		"""Change le status de l'utilisateur"""

		from log.logger import Log

		Log().add("[+] Client : le client " + str(self.client.getName()) + " a change son status en : " + str(args))
		self.client.status = args['args']
		return ('true')

	# {"cmd": "timeConnect", "args": "null"}
	@jsonPrototype('timeConnect')
	def __cmd_timeConnect(self, args):
		"""Retourne l'heure a laquelle c'est connecte le client"""

		from log.logger import Log

		Log().add("[+] Client : le client " + str(self.client.getName()) + " a demande l'heure de connection")
		return ('"' + str(self.client.connection_time) + '"')

	# {"cmd": "chanMasterPwd", "args": "NEWPASSWORD", "channel": "channelName", "app" : ""}
	@jsonPrototype('chanMasterPwd')
	def __cmd_chanMasterPwd(self, args):
		"""Change le mot de passe master d'un channel"""

		from log.logger import Log

		if self.client.master and self.client.room.changeChanMasterPwd(args, args['channel']):
			Log().add("[+] Client : le client " + str(self.client.getName()) + " a changer le mot de passe master du channel : " + args['app'])
			return ('true')
		else:
			if self.client.master == False:
				Log().add("[!] Command error : la commande chanMasterPwd a echoue ( le Client n'est pas master )", 'yellow')
			elif self.client.room.channelExists(args['args']) == False:
				Log().add("[!] Command error : la commande chanMasterPwd a echoue ( le channel n'existe pas )", 'yellow')
			else:
				Log().add("[!] Command error : la commande chanMasterPwd a echoue", 'yellow')
			return ('false')

	def status(self, client, master = False):
		"""
		Envoie le status aux clients lors d'une action ( join / part ... connect ...)
		"""

		from log.logger import Log

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
					name = client.getName()
					to_send = {"name": name, "key": key, "status": status}
					Log().add("[+] Client : envoie du status de " + name + " vers l'utilisateur : " + master.getName())
					json = Protocol.forgeJSON('status', simplejson.JSONEncoder().encode(to_send), {'channel': channel})
					master.addResponse(json)
			else:
				for user in channel.client_list:
					if user.master != client:
						status = client.status
						key = client.unique_key
						name = client.getName()
						to_send = {"name": name, "key": key, "status": status}
						Log().add("[+] Client : envoie du status master vers l'utilisateur : " + name)
						json = Protocol.forgeJSON('status', simplejson.JSONEncoder().encode(to_send), {'channel': client.room_name})
						user.addResponse(json)
