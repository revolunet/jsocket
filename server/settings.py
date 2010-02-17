##
# settings.py
##

class SETTINGS(object):
	"""docstring for SETTINGS"""
	def __init__(self):
		pass
	
	IS_DEBUG = True
	
	SERVER_PORT = 9999
<<<<<<< HEAD
	SERVER_HOST = '192.168.1.35'
=======
	SERVER_HOST = 'localhost'
>>>>>>> 265ea6ab7171d1f11d1313f71ed944c4d50828e0
	SERVER_SELECT_TIMEOUT = 5
	
	MAX_SENDQUEUE = 8
	MAX_RECEIVEQUEUE = 8
	
	MASTER_PASSWORD = 'admin'