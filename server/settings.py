##
# settings.py
##

class SETTINGS(object):
	"""docstring for SETTINGS"""
	def __init__(self):
		pass
	
	IS_DEBUG = True
	
	SERVER_PORT = 9999
	SERVER_HOST = 'localhost'
	SERVER_SELECT_TIMEOUT = 5
	SERVER_MAX_READ = 1024
	
	MAX_SENDQUEUE = 8
	MAX_RECEIVEQUEUE = 8
	
	MASTER_PASSWORD = 'admin'