##
# main.py
##

import socket
import SocketServer
import threading
import sys

from server.tcp import ServerTCP
from server.http import ServerHTTP
from server.watchdog import WatchDog
from commons.worker import WorkerReceive, WorkerSend
from commons.room import Room
from commons.session import Session
from log.logger import Log
import Queue

def mainTCP(room, squeue, rqueue, client_list, http_list):
	"""Lance un serveur TCP"""
	serverTCP = ServerTCP(room, squeue, rqueue, client_list, http_list)
	serverTCP.start()

def mainHTTP(room, squeue, rqueue, client_list, http_list, session):
	"""Lance un serveur HTTP"""
	serverHTTP = ServerHTTP(room, squeue, rqueue, client_list, http_list, session)
	serverHTTP.start()

if __name__ == '__main__':
	client_list = {'http': {}, 'tcp': {}}
	http_list = { }
	room = Room()
	squeue = Queue.Queue(4)
	WorkerSend(squeue).start()
	rqueue = Queue.Queue(4)
	WorkerReceive(rqueue).start()
	session = Session()

	mainTCP(room, squeue, rqueue, client_list, http_list)
	mainHTTP(room, squeue, rqueue, client_list, http_list, session)

	watchdog = WatchDog(client_list, session)
	watchdog.start()
	try:
		while (sys.stdin.readline()):
			pass
	except KeyboardInterrupt:
		print 'Hey !'
		exit()
