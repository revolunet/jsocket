import time

class History(object):
	def __init__(self):
		self.__history = []
		
	def add(self, uid, json):
		self.__history.append({
			'time': time.time(),
			'uid': uid,
			'json': json
		})
	
	def get(self):
		return self.__history
		
	def get_from(self, start, end):
		history = []
		for h in self.__history:
			if h.time <= start and h.time >= end:
				history.append(h)
		return history
		
	def flush(self):
		self.__history = []