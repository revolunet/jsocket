##
# watchdog.py
##

import threading
import datetime
import time
from log.logger import Log

class WatchDog(threading.Thread):
	def __init__(self, client_list):
		self.client_list = client_list
		self.isRunning = True
		self.sleepTime = 2
		self.maxIdleTime = 5
		Log().add("[+] WatchDog launched")
		
		threading.Thread.__init__(self)
	
	def run(self):
		while self.isRunning:
			current_time = datetime.datetime.now()
			for c in self.client_list['http']:
				if int(current_time.strftime("%S")) - int(c.last_action.strftime("%S")) > self.maxIdleTime:
					self.pop(c)
			time.sleep(self.sleepTime)
	
	def pop(self, client):
		Log().add("[+] Watching http client : "+client.unique_key+", last action: "+client.last_action.ctime())