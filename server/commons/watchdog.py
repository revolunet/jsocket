##
# watchdog.py
##

import threading
import time
from log.logger import Log
from threading import Lock
from config.settings import SETTINGS
from commons.session import Session

class WatchDog(threading.Thread):
	def __init__(self):
		self.lock = Lock()
		Log().add("[+] WatchDog: launched", 'green')
		threading.Thread.__init__(self)

	def run(self):
		while True:
			current_time = int(time.time())
			clients = Session().gets()
			uidToDelete = [ ]
			Log().add('[i] WatchDog: Server hosts %d clients' % len(clients), 'yellow')
			for (uid, client) in clients:
				if int(current_time - client.last_action) > SETTINGS.WATCHDOG_MAX_IDLE_TIME:
					uidToDelete.append(client.unique_key)
			if len(uidToDelete) > 0:
				Log().add('[i] WatchDog: Deleted %d clients' % len(uidToDelete), 'blue')
				self.lock.acquire()
				for uid in uidToDelete:
					Session().delete(uid)
				self.lock.release()
			del clients
			del uidToDelete
			time.sleep(SETTINGS.WATCHDOG_SLEEP_TIME)
