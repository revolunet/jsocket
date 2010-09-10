import simplejson
import Queue
from commons.worker import WorkerParser
from commons.session import Session
from log.logger import Log
from config.settings import SETTINGS
from commons.protocol import Protocol

class ApprovalProtocol(object):
	"""
	Classe permettant de valider les commandes JSON envoyee par le client
	"""

	def __init__(self):
		self.commands = {
			'refresh': lambda l:True,
			'connected':  lambda l:True,
			'history':  self.default,
			'auth':  self.default,
			'create':  self.default,
			'join':  self.default,
			'chanMasterPwd':  self.default,
			'chanAuth':  self.default,
			'nick':  self.default,
			'forward':  self.default,
			'list':  self.default,
			'message':  self.default,
			'setStatus':  self.default,
			'getStatus':  self.default,
			'timeConnect':  self.default,
			'part':  self.default,
			'remove':  self.default,
			'httpCreateChannel': lambda l:True
		}

	def default(self, json):
		""" Retourne True si la commande json comprend toute les keys obligatoires """
		return  json.get('args', None) is not None and \
				json.get('uid', None) is not None and \
				json.get('channel', None) is not None and \
				json.get('app', None) is not None

class Approval(object):
	"""
	Classe permettant de faire valider les commandes json ainsi que de recuperer les reponses
	"""

	instance = None

	def __new__(this):
		if this.instance is None:
			this.instance = object.__new__(this)
			this.session = Session()
			this.jsonProtocol = Protocol()
			this.queue = Queue.Queue(SETTINGS.WORKER_QUEUE_SIZE)
			for i in range(0, SETTINGS.WORKER_THREADING_SIZE):
				WorkerParser(this.queue, this.session, this.jsonProtocol).start()
			this.protocol = ApprovalProtocol()
		return this.instance

	def httpCreateChannel(self, cmd):
		try:
			uid = Session().create(None, 'http')
			decoded = simplejson.loads(cmd)
			if decoded.get('cmd', None) is not None:
				return self.jsonProtocol.parse(Session().get(uid), decoded)
		except ValueError:
			print 'Error'

	def validate(self, datas, callback = None, type = None):
		""" Valide la/les commande(s) json envoyees """
		if len(datas) == 0:
			pass

		data_list = self._split(datas)
		valid_cmd = []

		for cmd in data_list:
			try:
				decoded = simplejson.loads(cmd)
				if decoded.get('cmd', None) is not None:
					if self.validate_protocol(decoded):
						valid_cmd.append(decoded)
					else:
						pass
			except ValueError:
				Log().add("[!] Approval: JSON error %s" % str(datas), "red")
		if len(valid_cmd) > 0:
			uid = valid_cmd[0].get('uid', None)
			if uid is None:
				uid = Session().create(callback, type)
			self.queue.put({'json': valid_cmd, 'callback': callback, 'uid': uid, 'type': type})
			return uid
		return None

	def validate_protocol(self, decoded):
		""" Valide la commande via l':func:`ApprovalProtocol` """
		if decoded.get('cmd', None) is not None and self.protocol.commands.get(decoded['cmd'], None) is not None:
			return self.protocol.commands[decoded.get('cmd')](decoded)
		return False

	def _split(self, datas):
		datas = datas.split("\n")
		return [cmd for cmd in datas if len(cmd.strip()) > 0]