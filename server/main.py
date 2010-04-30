##
# main.py
##

import socket
import SocketServer
import threading
import sys

from server.twisted_tcp import ServerTCP
from server.http import ServerHTTP
#from server.watchdog import WatchDog
from commons.worker import WorkerParser
from commons.room import Room
from commons.session import Session
from log.logger import Log
import Queue

def mainTCP():
	"""Lance un serveur TCP"""
	serverTCP = ServerTCP()
	serverTCP.start()

def mainHTTP():
	"""Lance un serveur HTTP"""
	serverHTTP = ServerHTTP()
	serverHTTP.start()

if __name__ == '__main__':
	#room = Room()
	#WorkerSend(squeue).start()
	#rqueue = Queue.Queue(4)
	#WorkerReceive(rqueue).start()

	mainTCP()
	#mainHTTP()

	#watchdog = WatchDog(client_list, session)
	#watchdog.start()
	try:
		while (sys.stdin.readline()):
			pass
	except KeyboardInterrupt:
		print 'Hey !'
		exit()
