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
		self.maxIdleTime = 5
		self.lock = Lock()
		Log().add("[+] WatchDog launched")
		
		threading.Thread.__init__(self)
	
	def run(self):
		while self.isRunning:
			current_time = datetime.datetime.now()
			client_to_delete = []
			for key in self.client_list['http']:
				client = self.client_list['http'][key]
				if client.validJson == False or int(current_time.strftime("%S")) - int(client.last_action.strftime("%S")) > self.maxIdleTime:
					client_to_delete.append(key)
			for k in client_to_delete:
				self.pop(k)
			time.sleep(self.sleepTime)
	
	def pop(self, key):
		client = self.client_list['http'][key]
		Log().add("[+] WatchDog deleted http client : "+client.unique_key+", last action: "+client.last_action.ctime())
		self.lock.acquire()
		self.client_list['http'].pop(key)
		self.lock.release()