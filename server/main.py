##
# main.py
##

import socket
import SocketServer
import threading

from server.tcp import ServerTCP
from server.http import ServerHTTP
from commons.worker import Worker
from commons.room import Room
from log.logger import Log
import Queue

def mainTCP(room, squeue, rqueue):
	"""Lance un serveur TCP"""
	serverTCP = ServerTCP(room, squeue, rqueue)
	try:
		serverTCP.start()
	except KeyboardInterrupt:
		Log().add("[-] TCP Server Killed", 'ired')
		exit()

def mainHTTP(room, squeue, rqueue):
	"""Lance un serveur HTTP"""
	serverHTTP = ServerHTTP(room, squeue, rqueue)
	try:
		serverHTTP.start()
	except KeyboardInterrupt:
		Log().add("[-] HTTP Server Killed", 'ired')
		exit()

#if __name__ == '__main__':
#	main()	

if __name__ == '__main__':
	room = Room()
	squeue = Queue.Queue(0)
	Worker(squeue, 'send').start()
	rqueue = Queue.Queue(0)
	Worker(rqueue, 'recv').start()
	
	mainTCP(room, squeue, rqueue)
	mainHTTP(room, squeue, rqueue)
#	from server.http import ServerHTTP
	
#	server_http = ServerHTTP([], [], [])
#	server_http.start()