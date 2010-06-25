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
		if param.get('toUid', None) is not None:
			json += ', "toUid": "' + param['toUid'] + '"'
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
			'chanMasterPwd' : self.__cmd_chanMasterPwd,
			'history' : self.__cmd_history
		}

	def parse(self, client, json):
		"""Parsing de l'entre json sur le serveur"""
		self.uid = client.unique_key

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

		from commons.session import Session

		str = [ ]
		channelName = args['channel']
		appName = args['app']
		if args['channel'] is None:
			users = self.client.room.list_users(channelName=args, appName=appName)
		else:
			users = self.client.room.list_users(channelName=channelName, appName=appName)
		for u in users:
			user = Session().get(u)
			if user is not None:
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

		channelName = args['args']
		appName = args['app']
		if self.client.room.remove(channelName=channelName, appName=appName):
			Log().add("[+] Le channel " + channelName + " a ete supprime par : " + str(self.client.getName()))
			return ('true')
		else:
			Log().add("[!] Command error : la commande delete a echoue ( le channel " + channelName + " n'existe pas )", 'yellow')
			return ('false')

	# {"cmd": "create", "args": ["irc", "appPwd"], "channel": "", "app" : ""}
	@isMaster('create')
	@jsonPrototype('create')
	def __cmd_create(self, args):
		"""Creation d'un nouveau channel si le Client est Master"""

		from log.logger import Log

		appName = args['app']
		channelName = args['args'][0]
		password = args['args'][1]
		if self.client.room.create(channelName=channelName, appName=appName, password=password, uid=self.uid):
			Log().add("[+] Le channel %s a ete ajoute par : %s"  % ( channelName,  str(self.client.getName())))
			return ('"' + str(self.client.room.Channel(channelName=channelName, appName=appName).master_password) + '"')
		else:
			Log().add("[!] Command error : la commande create a echoue ( le channel existe deja )", 'yellow')
			return ('false')

	# {"cmd": "history", "args": ["irc", "appPwd"], "channel": "", "app" : ""}
	@jsonPrototype('history')
	def __cmd_history(self, args):

		appName = args['app']
		channelName = args['channel']

		history = self.client.room.history(appName=appName, channelName=channelName)
		if len(history) > 0:
			return (simplejson.JSONEncoder().encode(history))
		return (simplejson.JSONEncoder().encode([]))

	# {"cmd": "join", "args": ["irc", ""]}
	@jsonPrototype('join')
	def __cmd_join(self, args):
		"""Ajoute un client dans le salon specifie"""

		from log.logger import Log

		appName = args['app']
		channelName = args['args'][0]
		password = args['args'][1]
		if len(password) == 0:
			password = None
		if self.client.room.join(channelName=channelName, appName=appName, uid=self.uid, password=password):
			self.client.room_name = channelName
			Log().add("[+] Client : l'utilisateur " + str(self.client.getName()) + " a rejoin le channel : " + channelName, 'yellow')
			if self.client.master == False:
				self.status(client=self.client, appName=appName, master=False)
			else:
				self.status(client=self.client, appName=appName, master=True)
			return ('true')
		else:
			Log().add("[!] Command error : le channel " + channelName + " n'existe pas ", 'yellow')
			return ('false')

	# {"cmd": "part", "args": "irc"}
	@jsonPrototype('part')
	def __cmd_part(self, args):
		"""Supprime un client du salon specifie"""

		from log.logger import Log

		channelName = args['args']
		appName = args['app']
		if self.client.room_name and self.client.room.part(channelName=channelName, appName=appName, uid=self.uid):
			self.client.status = "offline"
			Log().add("[+] Client : le client " + str(self.client.getName()) + " a quitte le channel : " + channelName)
			if self.client.master == False:
				self.status(client=self.client, appName=appName, master=False)
			else:
				self.status(client=self.client, appName=appName, master=True)
			self.client.room_name = None
			return ('true')
		else:
			Log().add("[!] Command error : l'utilisateur n'est pas dans le channel : " + channelName)
			return ('false')

	# {"cmd": "chanAuth", "args": "passphrase", "channel": "channelName", "app" : ""}
	@jsonPrototype('chanAuth')
	def __cmd_chanAuth(self, args):
		"""Auth pour definir si le Client est desormais master ou non d'une application"""

		from log.logger import Log

		appName = args['app']
		channelName = args['channel']
		password = args['args']
		if self.client.room.appAuth(channelName=channelName, appName=appName, password=password, uid=self.uid):
			Log().add("[+] Client : le client " + str(self.client.getName()) + " est a present master du channel : " + channelName)
			return ('true')
		else:
			return ('false')

	# {"cmd": "forward", "args": "message", "channel": "channelName", "app" : ""}
	@isMaster('forward')
	@jsonPrototype('forward')
	def __cmd_forward(self, args):
		"""Envoie une commande a tous les clients presents dans le channel"""

		from log.logger import Log

		channelName = args['channel']
		appName = args['app']
		commande = args['args']
		app = args['app']
		if args['channel'] and args['app'] and self.client.room.forward(channelName=channelName, appName=appName, commande=commande, uid=self.uid, app=app):
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

		import urllib
		from log.logger import Log

		message = args.get('args', '')
		channelName = args['channel']
		appName = args['app']
		if len(message) == 0:
			return ('false')
		else:
			ret = False
			if len(message[0]) != 0:
				if len(message[1]) > 0:
					if len(message[1][0]) == 0:
						ret = self.client.room.message(channelName=channelName, appName=appName, sender=self.uid, users=['master'], message=message[0])
					elif message[1][0] == '*':
						ret = self.client.room.message(channelName=channelName, appName=appName, sender=self.uid, users=['all'], message=message[0])
					elif message[1][0] == 'master':
						ret = self.client.room.message(channelName=channelName, appName=appName, sender=self.uid, users=['master'], message=message[0])
					else:
						ret = self.client.room.message(channelName=channelName, appName=appName, sender=self.uid, users=message[1], message=message[0])
				else:
					ret = self.client.room.message(channelName=channelName, appName=appName, sender=self.uid, users=['master'], message=message[0])
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

		appName = args['app']

		Log().add("[+] Client : le client " + str(self.client.getName()) + " a change son status en : " + str(args))
		self.client.status = args['args']
		if self.client.master == False:
			self.status(client=self.client, appName=appName, master=False)
		else:
			self.status(client=self.client, appName=appName, master=True)
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

		channelName = args['channel']
		password = args['args']
		appName = args['app']

		if self.client.master and self.client.room.changeAppMasterPwd(channelName=channelName, appName=appName, password=password):
			Log().add("[+] Client : le client " + str(self.client.getName()) + " a changer le mot de passe master du channel : " + channelName)
			return ('true')
		else:
			if self.client.master == False:
				Log().add("[!] Command error : la commande chanMasterPwd a echoue ( le Client n'est pas master )", 'yellow')
			elif self.client.room.chanExists(channelName=channelName, appName=appName) == False:
				Log().add("[!] Command error : la commande chanMasterPwd a echoue ( le channel n'existe pas )", 'yellow')
			else:
				Log().add("[!] Command error : la commande chanMasterPwd a echoue", 'yellow')
			return ('false')

	def status(self, client, appName, master = False):
		"""
		Envoie le status aux clients lors d'une action ( join / part ... connect ...)
		"""

		from log.logger import Log
		from commons.session import Session

		if client.room_name:
			channel = client.room.Channel(channelName=client.room_name, appName=appName)
			if channel and master == False:
				masters = channel.masters()
				for master in masters:
					if client.room_name:
						channel = client.room_name
					else:
						channel = "none"
					master = Session().get(master)
					if master is not None:
						status = client.status
						key = client.unique_key
						name = client.getName()
						to_send = {"name": name, "key": key, "status": status}
						Log().add("[+] Client : envoie du status de " + name + " vers l'utilisateur : " + master.getName())
						json = Protocol.forgeJSON('status', simplejson.JSONEncoder().encode(to_send), {'channel': channel})
						master.addResponse(json)
			elif channel is not None:
				for u in channel.users():
					user = Session().get(u)
					if user is not None and user.master != client:
						status = client.status
						key = client.unique_key
						name = client.getName()
						to_send = {"name": name, "key": key, "status": status}
						Log().add("[+] Client : envoie du status master vers l'utilisateur : " + name)
						json = Protocol.forgeJSON('status', simplejson.JSONEncoder().encode(to_send), {'channel': client.room_name})
						if user is not None:
							user.addResponse(json)
