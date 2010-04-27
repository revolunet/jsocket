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
		from client.client import Client

		client = Client(self.room)
		self.clientList[client.unique_key] = client
		return client.unique_key

	def get(self, uid = None):
		if uid is not None:
			return self.clientList.get(uid, None)
		return None

	def delete(self, uid):
		if self.clientList.get(uid, None) is not None:
			del self.clientList[uid]
			return True
		return False
