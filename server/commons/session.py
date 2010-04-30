from commons.room import Room

class Session(object):
	instance = None

	def __new__(this):
		if this.instance is None:
			this.instance = object.__new__(this)
		return this.instance

	def __init__(self):
		self.room = Room()
		self.clientList = { }

	def create(self):
		from log.logger import Log
		from client.client import Client
		
		client = Client(self.room)
		self.clientList[client.unique_key] = client
		Log().add('[+] Session: Add/Update client %s' % (client.unique_key))
		return self.clientList[client.unique_key]

	def getFromJson(self, json):
		if json.get('uid', None) is not None:
			return self.get(json['uid'])
		return self.create()

	def get(self, uid = None):
		if uid is not None:
			return self.clientList.get(uid, None)
		return None
