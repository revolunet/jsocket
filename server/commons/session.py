##
# session.py
##

from log.logger import Log

class Session(object):
	def __init__(self):
		self.__client_list = { }
		self.__client_vars = [
			'room',
			'master',
			'nickName',
			'status',
			'connection_time',
			'last_action',
			'room_name'
		]

	def set(self, uid, client):
		self.__client_list[uid] = { }
		for var in self.__client_vars:
			self.__client_list.get(uid)[var] = getattr(client, var)
		Log().add('[+] Session: Add/Update client %s' % (uid))
		
		return True

	def get(self, uid):
		return self.__client_list.get(uid, None)

	def restore(self, uid, clientObject):
		client = self.get(uid)
		if client is None:
			return False
		for var in self.__client_vars:
			setattr(clientObject, var, client.get(var))
		Log().add('[i] Session: Restore client %s' % (uid))
		return True

	def update(self, uid, clientObject):
		client = self.set(uid, clientObject)