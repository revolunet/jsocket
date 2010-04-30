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
			client_session_to_delete = []
			for key in self.client_list['http']:
				client = self.client_list['http'][key]
				if client.validJson == False:
					client_to_delete.append({'key':key, 'reason':'json'})
				elif int(current_time - client.last_action) > self.maxIdleTime:
					client_to_delete.append({'key':key, 'reason':'time'})
				session_list = self.session.get()
			for k in session_list:
				clientSession = self.session.get(k)
				if clientSession is not None:
					if int(current_time - clientSession.get('last_action', 0)) > self.maxIdleTime:
						client_session_to_delete.append({'key':k, 'reason':'time'})
			for d in client_to_delete:
				self.pop(d)
			for c in client_session_to_delete:
				self.sessionPop(c)
			time.sleep(self.sleepTime)

	def pop(self, d):
		client = self.client_list['http'][d['key']]
		if d['reason'] == 'time':
			Log().add("[+] WatchDog deleted (inactif) http client : "+client.unique_key+", last action: "+ str(client.last_action))
		elif d['reason'] == 'json':
			Log().add("[+] WatchDog deleted (invalid json) http client : "+client.unique_key+", last action: "+ str(client.last_action))
		self.lock.acquire()
		if client.client_socket != None:
			client.client_socket.close()
		client.join()
		self.client_list['http'].pop(d['key'])
		self.lock.release()

	def sessionPop(self, d):
		current_time = int(time.time())
		clientSession = self.session.get(d['key'])
		if clientSession is not None:
			last_action = clientSession.get('last_action', 0)
			if int(current_time - last_action) > self.maxIdleTime:
				success = self.session.pop(d['key'])
				if success:
					if d['reason'] == 'time':
						Log().add("[+] WatchDog deleted (inactif) session : "+d['key']+", last action: "+ str(last_action))
					elif d['reason'] == 'json':
						Log().add("[+] WatchDog deleted (invalid json) session : "+d['key']+", last action: "+ str(last_action))
