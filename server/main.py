##
# main.py
##

import socket
import SocketServer
import threading

from server.tcp import ServerTCP

def main():
	"""Lance un serveur TCP"""
	server = ServerTCP()
	try:
		server.start()
	except KeyboardInterrupt:
		exit()

#if __name__ == '__main__':
#	main()	

if __name__ == '__main__':
	main()
#	from server.http import ServerHTTP
	
#	server_http = ServerHTTP([], [], [])
#	server_http.start()