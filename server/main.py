##
# main.py
##

import socket
import SocketServer
import threading
import sys

from server.tcp import ServerTCP
from server.http import ServerHTTP
#from server.watchdog import WatchDog
from commons.worker import WorkerParser

def mainTCP():
	"""Lance un serveur TCP"""
	serverTCP = ServerTCP()
	serverTCP.start()

def mainHTTP():
	"""Lance un serveur HTTP"""
	serverHTTP = ServerHTTP()
	serverHTTP.start()

if __name__ == '__main__':
	mainHTTP()
	mainTCP()
	#watchdog = WatchDog(client_list, session)
	#watchdog.start()
	try:
		while (sys.stdin.readline()):
			pass
	except KeyboardInterrupt:
		print 'Hey !'
		exit()
