##
# watchdog.py
##

import threading
import time
from log.logger import Log
from threading import Lock

class WatchDog(threading.Thread):
	def __init__(self, client_list, session):
		self.client_list = client_list
		self.session = session
		self.isRunning = True
		self.sleepTime = 2
		self.maxIdleTime = 10
		self.lock = Lock()
		Log().add("[+] WatchDog launched")
		
		threading.Thread.__init__(self)
	
	def run(self):
		while self.isRunning:
			current_time = int(time.time())
			client_to_delete = []
			for key in self.client_list['http']:
				client = self.client_list['http'][key]
				if client.validJson == False:
					client_to_delete.append({'key':key, 'reason':'json'})
				elif (current_time - client.last_action) > self.maxIdleTime:
					client_to_delete.append({'key':key, 'reason':'time'})
			for d in client_to_delete:
				self.sessionPop(d)
				self.pop(d)
			time.sleep(self.sleepTime)
	
	def pop(self, d):
		client = self.client_list['http'][d['key']]
		if d['reason'] == 'time':
			Log().add("[+] WatchDog deleted (inactif) http client : "+client.unique_key+", last action: "+client.last_action.ctime())
		elif d['reason'] == 'json':
			Log().add("[+] WatchDog deleted (invalid json) http client : "+client.unique_key+", last action: "+client.last_action.ctime())
		self.lock.acquire()
		if client.client_socket != None:
			client.client_socket.close()
		client.join()
		self.client_list['http'].pop(d['key'])
		self.lock.release()
	
	def sessionPop(self, d):
		current_time = int(time.time())
		client = self.client_list['http'][d['key']]
		clientSession = self.session.get(client.unique_key)
		if (current_time - clientSession.get('last_action', 0)) > self.maxIdleTime:
			success = self.session.pop(client.unique_key)
			if success:
				if d['reason'] == 'time':
					Log().add("[+] WatchDog deleted (inactif) session : "+client.unique_key+", last action: "+client.last_action.ctime())
				elif d['reason'] == 'json':
					Log().add("[+] WatchDog deleted (invalid json) session : "+client.unique_key+", last action: "+client.last_action.ctime())
