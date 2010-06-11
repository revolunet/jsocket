##
# main.py
##

import sys
import time

from server.tcphttp import ServerTwisted
from commons.watchdog import WatchDog
from twisted.internet import reactor

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
		print 'Please wait few seconds. Exiting...'
		#watchdog.kill()
		#watchdog.join()
		reactor.stop()
		sys.exit(0)
