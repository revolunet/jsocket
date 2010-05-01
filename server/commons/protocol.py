import simplejson

def isMaster(attrs):
	def _isMaster(f):
		def decorated(self, *args, **kwargs):
			if self.client.master:
				return f(self, *args, **kwargs)
			return ('{"from": "'+attrs+'", "value": false, "message": "Vous n%22etes pas administrateur du serveur."}')
		return decorated
	return _isMaster

class Protocol(object):
	"""docstring for Protocol"""
	def __init__(self):
		from log.logger import Log
		self.client = None
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
	def __cmd_connected(self, args = None):
		"""Le client est connecte, sa cle unique lui est send"""

		return ('{"from": "connected", "value": "' + str(self.client.unique_key) + '"}')

	# {"cmd" : "auth", "args": "masterpassword", "channel": "", "app" : ""}
	def __cmd_auth(self, args):
		"""
		Authentifie un client en tant que master du server.
		"""

		from log.logger import Log

		if args['args'] == self.client.master_password:
			self.client.master = True
			Log().add("[+] Client : le client " + str(self.client.getName()) + " est a present master du serveur")
			return ('{"from": "auth", "value": true, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
		return ('{"from": "auth", "value": false, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')

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
			name = user.getName()
			to_send = {"name": name, "key": key, "status": status}
			str.append(to_send)
		return ('{"from": "list", "value": ' + simplejson.JSONEncoder().encode(str) + ', "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')

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
	def __cmd_remove(self, args):
		"""On supprimet un channel, si celui si existe et que Client est Master"""

		from log.logger import Log

		if self.client.room.remove(args['args']):
			Log().add("[+] Le channel " + args['args'] + " a ete supprime par : " + str(self.client.getName()))
			return ('{"from": "remove", "value": true, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
		else:
			Log().add("[!] Command error : la commande delete a echoue ( le channel " + args['args'] + " n'existe pas )", 'yellow')
			return ('{"from": "remove", "value": false, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')

	# {"cmd": "create", "args": ["irc", "appPwd"], "channel": "", "app" : ""}
	@isMaster('create')
	def __cmd_create(self, args):
		"""Creation d'un nouveau channel si le Client est Master"""

		from log.logger import Log

		if self.client.room.create(args['args'], self.client):
			Log().add("[+] Un nouveau channel a ete ajoute par : " + str(self.client.getName()))
			return ('{"from": "create", "value": "'+str(self.client.room.channel(args['args'][0]).masterPwd)+'", "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
		else:
			Log().add("[!] Command error : la commande create a echoue ( le channel existe deja )", 'yellow')
			return ('{"from": "create", "value": false, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')

	# {"cmd": "join", "args": ["irc", ""]}
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
			return ('{"from": "join", "value": true, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
		else:
			Log().add("[!] Command error : le channel " + args['args'][0] + " n'existe pas ", 'yellow')
			return ('{"from": "join", "value": false, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')

	# {"cmd": "part", "args": "irc"}
	def __cmd_part(self, args):
		"""Supprime un client du salon specifie"""

		from log.logger import Log

		if self.client.room_name and self.client.room.part(args['args'], self.client):
			self.client.room_name = None
			self.client.status = "offline"
			Log().add("[+] Client : le client " + str(self.client.getName()) + " a quitte le channel : " + args['args'])
			if self.client.master == False:
				self.status(self.client)
			return ('{"from": "part", "value": true, "channel": "'+args['args']+'", "app": "'+args['app']+'"}')
		else:
			Log().add("[!] Command error : l'utilisateur n'est pas dans le channel : " + args['args'])
			return ('{"from": "part", "value": false, "channel": "'+args['args']+'", "app": "'+args['app']+'"}')

	# {"cmd": "chanAuth", "args": "passphrase", "channel": "channelName", "app" : ""}
	def __cmd_chanAuth(self, args):
		"""Auth pour definir si le Client est desormais master ou non d'une application"""

		from log.logger import Log

		if self.client.room.chanAuth(args['channel'], args['args'], self.client):
			Log().add("[+] Client : le client " + str(self.client.getName()) + " est a present master du channel : " + args['channel'])
			return ('{"from": "chanAuth", "value": true, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
		else:
			return ('{"from": "chanAuth", "value": false, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')

	# {"cmd": "forward", "args": "message", "channel": "channelName", "app" : ""}
	@isMaster('forward')
	def __cmd_forward(self, args):
		"""Envoie une commande a tous les clients presents dans le channel"""

		from log.logger import Log

		if args['channel'] and args['app'] and self.client.room.forward(args['channel'], args['args'], self.client, args['app']):
			Log().add("[+] La commande : "+ args['args'] + " a ete envoye a tous les utilisateurs du channel : " + str(args['channel']))
			return ('{"from": "forward", "value": true, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
		else:
			if self.client.room_name is None:
				Log().add("[!] Command error : la commande forward a echoue ( le Client n'est dans aucun channel )", 'yellow')
			else:
				Log().add("[!] Command error : la commande forward a echoue ( Aucun autre client dans le salon )", 'yellow')
			return ('{"from": "forward", "value": false, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')

	# {"cmd": "message", "args": ['mon message', ['*']], "channel": "channelName", "app" : "" }
	def __cmd_message(self, args):
		"""Envoie un message a une liste d'utilisateurs"""

		message = args['args']
		if len(message) == 0:
			return ('{"from": "message", "value": false, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
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
				return ('{"from": "message", "value": true, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
			else:
				return ('{"from": "message", "value": false, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')

	# {"cmd": "nick", "args": "nickName", "app": "appName"}
	def __cmd_nick(self, args):
		"""Permet au client de change de pseudo"""

		from log.logger import Log

		Log().add("[+] Client : le client " + str(self.client.getName()) + " a change son nickname en : " + args['args'])
		self.client.nickName = args['args']
		return ('{"from": "nick", "value": true, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')

	# {"cmd": "getStatus", "args": "null"}
	def __cmd_getStatus(self, args):
		"""Retourne le status de l'utilisateur"""

		from log.logger import Log

		Log().add("[+] Client : le client " + str(self.client.getName()) + " a demande son status")
		return ('{"from": "getStatus", "value": "' + self.client.status + '", "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')

	# {"cmd": "setStatus", "args": "newStatus"}
	def __cmd_setStatus(self, args):
		"""Change le status de l'utilisateur"""

		from log.logger import Log

		Log().add("[+] Client : le client " + str(self.client.getName()) + " a change son status en : " + str(args))
		self.client.status = args['args']
		return ('{"from": "setStatus", "value": true, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')

	# {"cmd": "timeConnect", "args": "null"}
	def __cmd_timeConnect(self, args):
		"""Retourne l'heure a laquelle c'est connecte le client"""

		from log.logger import Log

		Log().add("[+] Client : le client " + str(self.client.getName()) + " a demande l'heure de connection")
		return ('{"from": "timeConnect", "value": "' + str(self.client.connection_time) + '", "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')

	# {"cmd": "chanMasterPwd", "args": "NEWPASSWORD", "channel": "channelName", "app" : ""}
	def __cmd_chanMasterPwd(self, args):
		"""Change le mot de passe master d'un channel"""

		from log.logger import Log

		if self.client.master and self.client.room.changeChanMasterPwd(args, args['channel']):
			Log().add("[+] Client : le client " + str(self.client.getName()) + " a changer le mot de passe master du channel : " + args['app'])
			return ('{"from": "chanMasterPwd", "value": true, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')
		else:
			if self.client.master == False:
				Log().add("[!] Command error : la commande chanMasterPwd a echoue ( le Client n'est pas master )", 'yellow')
			elif self.client.room.channelExists(args['args']) == False:
				Log().add("[!] Command error : la commande chanMasterPwd a echoue ( le channel n'existe pas )", 'yellow')
			else:
				Log().add("[!] Command error : la commande chanMasterPwd a echoue", 'yellow')
			return ('{"from": "chanMasterPwd", "value": false, "channel": "'+args['channel']+'", "app": "'+args['app']+'"}')

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
					master.addResponse('{"from": "status", "value": '+ simplejson.JSONEncoder().encode(to_send) +', "channel": "'+channel+'"}')
			else:
				for user in channel.client_list:
					if user.master != client:
						status = client.status
						key = client.unique_key
						name = client.getName()
						to_send = {"name": name, "key": key, "status": status}
						Log().add("[+] Client : envoie du status master vers l'utilisateur : " + name)
						user.addResponse('{"from": "status", "value": '+ simplejson.JSONEncoder().encode(to_send) +', "channel": "'+client.room_name+'"}')
