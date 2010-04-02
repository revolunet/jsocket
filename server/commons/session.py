##
# session.py
##

def session(object):
	def __init__(self):
		self.__client_list = { }

	def get(self, uid):
		if self.__client_list.get(uid) is not None:
			return self.__client_list.get(uid)
		return self.default()

	def set(self, uid, client):
		self.__client_list[uid] = client
		return True

	def default(self):
		pass