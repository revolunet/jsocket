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
	"""
	Classe permettant de nettoyer les clients inactifs.
	"""

	def __init__(self):
		self.lock = Lock()
		self.running = True
		Log().add("[+] WatchDog: launched", 'green')
		threading.Thread.__init__(self)
		self.setDaemon(True)

	def kill(self):
		self.running = False

	def run(self):
		total_client = -1
		room = None
		while self.running:
			if room is None and len(Session().gets()) > 0:
				clients = Session().gets()
				(uid, client) = clients[0]
				room = client.room
			if room is not None:
				self.removeRooms(room)
			total_client = self.removeClients(total_client)
			time.sleep(SETTINGS.WATCHDOG_SLEEP_TIME)

	def removeRooms(self, room):
		appToRemove = []
		for application in room.applications:
			for c in room.applications[application]:
				channel = c.get('channel')
				if len(channel.users()) == 0 and len(channel.masters()) == 0:
					room.remove(channelName=channel.name, appName=application)
					Log().add('[i] WatchDog: Deleted %s channel' % channel.name, 'blue')
				if len(room.applications[application]) == 0:
					appToRemove.append(application)
		for app in appToRemove:
			room.applications.pop(app)
			Log().add('[i] WatchDog: Deleted %s application' % app, 'blue')

	def checkHttpClient(self, current_time, client):
		if client.type is 'http' and int(current_time - client.last_action) > SETTINGS.WATCHDOG_HTTP_DISCONNECT_TIME:
			return False
		return True

	def removeClients(self, total_client):
		current_time = int(time.time())
		clients = Session().gets()
		uidToDelete = [ ]
		if len(clients) != total_client:
			total_client = len(clients)
			Log().add('[i] WatchDog: Server hosts %d clients' % len(clients), 'yellow')
		for (uid, client) in clients:
			if self.checkHttpClient(current_time, client) is False:
				uidToDelete.append(client.unique_key)
			elif int(current_time - client.last_action) > SETTINGS.WATCHDOG_MAX_IDLE_TIME:
				uidToDelete.append(client.unique_key)
		if len(uidToDelete) > 0:
			Log().add('[i] WatchDog: Deleted %d clients' % len(uidToDelete), 'blue')
			self.lock.acquire()
			for uid in uidToDelete:
				Session().delete(uid)
			self.lock.release()
		del clients
		del uidToDelete
		return total_client
