

class Filter(object):
	def __init__(self):
		self.__filters = []
		self.init_filters()
		
	def init_filters(self):
		self.filters.append({
			'filter': 'image...'
		})