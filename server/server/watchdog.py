##
# watchdog.py
##

import threading
import datetime
import time
from log.logger import Log
from threading import Lock

class WatchDog(threading.Thread):
	def __init__(self, client_list):
		self.client_list = client_list
		self.isRunning = True
		self.sleepTime = 2
		self.maxIdleTime = 60
		self.lock = Lock()
		Log().add("[+] WatchDog launched")
		
		threading.Thread.__init__(self)
	
	def run(self):
		while self.isRunning:
			current_time = datetime.datetime.now()
			client_to_delete = []
			for key in self.client_list['http']:
				client = self.client_list['http'][key]
				if client.validJson == False:
					client_to_delete.append({'key':key, 'reason':'json'})
				elif int(current_time.strftime("%S")) - int(client.last_action.strftime("%S")) > self.maxIdleTime:
					client_to_delete.append({'key':key, 'reason':'time'})
			for d in client_to_delete:
				#self.pop(d)
				pass
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
		self.client_list['http'].pop(d['key'])
		self.lock.release()