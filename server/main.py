##
# main.py
##

import sys

from server.tcphttp import ServerTwisted
from commons.watchdog import WatchDog

def mainTwisted():
	"""Lance un serveur HTTP et TCP"""
	serverTwisted = ServerTwisted()
	serverTwisted.start()

def mainWatchDog():
	"""Lance le watchdog"""
	watchdog = WatchDog()
	watchdog.start()

if __name__ == '__main__':
	mainTwisted()
	mainWatchDog()
	try:
		while (sys.stdin.readline()):
			pass
	except KeyboardInterrupt:
		print 'Hey !'
		exit()
