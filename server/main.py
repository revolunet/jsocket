##
# main.py
##

import socket
import SocketServer
import threading

from server import Server

def main():
	server = Server()
	try:
		server.start()
	except KeyboardInterrupt:
		exit()

if __name__ == '__main__':
	main()