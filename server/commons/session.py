from commons.room import Room

class Session(object):
	instance = None

	def __new__(this):
		if this.instance is None:
			this.instance = object.__new__(this)
			this.room = Room()
			this.clientList = { }
		return this.instance

	def create(self):
		from log.logger import Log
		from client.client import Client

		client = Client(self.room)
		self.clientList[client.unique_key] = client
		Log().add('[+] Session: Add/Update client %s' % (client.unique_key))
		return client.unique_key

	def get(self, uid = None):
		from log.logger import Log

		Log().add('session_get_uid: %s' % str(uid))
		Log().add('session_get_clientList: %s' % str(self.clientList))
		if uid is not None:
			return self.clientList.get(uid, None)
		return None
