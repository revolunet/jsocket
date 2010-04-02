##
# settings.py
##

import socket

class SETTINGS(object):
	"""
	Settings du / des servers 
	"""
	
	def __init__(self):
		pass
	
	IS_DEBUG = True
	
	SERVER_PORT = 9999
	SERVER_HOST = socket.gethostbyname(socket.gethostname())
	#SERVER_HOST = '192.168.1.34'
	
	HTTP_SERVER_NAME = 'Jsocket Server 1.0'

	SERVER_SELECT_TIMEOUT = 5
	SERVER_MAX_READ = 1024
	
	# Ne prends pas en compte le/les master/s
	CHANNEL_MAX_USERS = 100
	
	MAX_SENDQUEUE = 8
	MAX_RECEIVEQUEUE = 8
	
	MASTER_PASSWORD = 'admin'