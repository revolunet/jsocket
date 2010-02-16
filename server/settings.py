##
# settings.py
##

class SETTINGS(object):
	"""docstring for SETTINGS"""
	def __init__(self):
		pass
	
	IS_DEBUG = False
	
	SERVER_PORT = 9999
	SERVER_HOST = '192.168.1.34'
	SERVER_SELECT_TIMEOUT = 5
	
	MAX_SENDQUEUE = 8
	MAX_RECEIVEQUEUE = 8
	
	MASTER_PASSWORD = 'admin'