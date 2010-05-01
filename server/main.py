##
# main.py
##

import socket
import SocketServer
import threading
import sys

from server.tcp import ServerTCP
from server.http import ServerHTTP
from commons.watchdog import WatchDog
from commons.worker import WorkerParser

def mainTCP():
	"""Lance un serveur TCP"""
	serverTCP = ServerTCP()
	serverTCP.start()

def mainHTTP():
	"""Lance un serveur HTTP"""
	serverHTTP = ServerHTTP()
	serverHTTP.start()

def mainWatchDog():
	"""Lance le watchdog"""
	watchdog = WatchDog()
	watchdog.start()

if __name__ == '__main__':
	mainHTTP()
	mainTCP()
	mainWatchDog()
	try:
		while (sys.stdin.readline()):
			pass
	except KeyboardInterrupt:
		print 'Hey !'
		exit()
