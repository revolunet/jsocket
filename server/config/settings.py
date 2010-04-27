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
	SERVER_HTTP_PORT = 81
	#SERVER_HOST = socket.gethostbyname(socket.gethostname())
	SERVER_HOST = 'localhost'

	SERVER_SELECT_TIMEOUT = 5
	SERVER_MAX_READ = 1024
	SERVER_HTTP_CLIENT_TIMEOUT = 30 # !important

	# Ne prends pas en compte le/les master/s
	CHANNEL_MAX_USERS = 100

	MASTER_PASSWORD = 'admin'

	# THREADS CONFIGURATION
	LOG_QUEUE_NB_THREAD = 4
	WORKER_QUEUE_NB_THREAD = 4
