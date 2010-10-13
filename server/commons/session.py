from commons.room import Room
from commons.request import Request

class Session(object):
	instance = None

	def __new__(this):
		if this.instance is None:
			this.instance = object.__new__(this)
			this.room = Room()
			this.clientList = { }
		return this.instance

	def create(self, callback = None, connectionType = None, vhost = None):
		from client.client import Client

		client = Client(self.room)
		client.callback = callback
		client.type = connectionType
		if vhost:
			client.vhost = vhost       
		self.clientList[client.unique_key] = client
		return client.unique_key

	def get(self, uid = None):
		if uid is not None:
			return self.clientList.get(uid, None)
		return None

	def gets(self):
		return self.clientList.items()

	def delete(self, uid):
		if self.clientList.get(uid, None) is not None:
			client = self.clientList.get(uid, None)
			client.room.leaveRooms(uid)
			request = Request(client.vhost, uid, 'offline')
			del self.clientList[uid]
			request.start()
			# envoie du packet tcp
			return True
		return False