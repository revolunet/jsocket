import simplejson
from commons.worker import WorkerParser
from commons.session import Session
from log.logger import Log
import Queue

class ApprovalProtocol(object):
	def __init__(self):
		self.commands = {
			'refresh': self.default,
			'connected':  lambda l:True,
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
			'remove':  self.default
		}

	def default(self, json):
		return  json.get('args', None) is not None and \
				json.get('uid', None) is not None and \
				json.get('channel', None) is not None and \
				json.get('app', None) is not None

class Approval(object):

	instance = None

	def __new__(this):
		if this.instance is None:
			this.instance = object.__new__(this)
			this.queue = Queue.Queue(4)
			WorkerParser(this.queue).start()
			this.protocol = ApprovalProtocol()
			this.callback = None
		return this.instance

	def validate(self, datas, callback = None):
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
				print "[<] Json error -> %s " % str(datas)
		if len(valid_cmd) > 0:
			uid = valid_cmd[0].get('uid', None)
			if uid is None:
				uid = Session().create()
			self.queue.put({'json': valid_cmd, 'callback': callback, 'uid': uid})
			return uid
		return None

	def validate_protocol(self, decoded):
		if decoded.get('cmd') in self.protocol.commands:
			return self.protocol.commands[decoded.get('cmd')](decoded)
		return False

	def _split(self, datas):
		datas = datas.split("\n")
		commands = []
		for data in datas:
			data = data.strip()
			if len(data) > 0:
				commands.append(data)
		return commands
