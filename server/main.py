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
	return serverTwisted

def mainWatchDog():
	"""Lance le watchdog"""
	watchdog = WatchDog()
	watchdog.start()
	return watchdog

if __name__ == '__main__':
	serverTwisted = mainTwisted()
	watchdog = mainWatchDog()
	try:
		while (sys.stdin.readline()):
			pass
	except KeyboardInterrupt:
		print 'Hey !'
		watchdog.kill()
		watchdog.join()
		sys.exit()