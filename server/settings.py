##
# settings.py
##

class SETTINGS(object):
	"""docstring for SETTINGS"""
	def __init__(self):
		pass
	
	IS_DEBUG = True
	
	SERVER_PORT = 9999
	SERVER_HOST = '192.168.1.35'

>>>>>>> 75fe51653cf5e3ee38a130df10bd0a0bdf6f7331
	SERVER_SELECT_TIMEOUT = 5
	SERVER_MAX_READ = 1024
	
	# Ne prends pas en compte le/les master/s
	CHANNEL_MAX_USERS = 100
	
	MAX_SENDQUEUE = 8
	MAX_RECEIVEQUEUE = 8
	
	MASTER_PASSWORD = 'admin'
