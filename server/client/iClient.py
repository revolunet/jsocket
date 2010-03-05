
import threading
import time
import random
from config.settings import SETTINGS
from commons.protocol import Protocol

class IClient(threading.Thread):

	def __init__(self, room, rqueue, squeue, Ctype):
		self.protocol = Protocol(self)
		self.type = Ctype
		self.room = room
		self.master = False
		self.nickName = None
		self.master_password = SETTINGS.MASTER_PASSWORD
		self.unique_key = hex(random.getrandbits(64))
		self.rqueue = rqueue
		self.squeue = squeue
		self.status = 'online'
		self.connection_time = time.time()
		self.room_name = None
		threading.Thread.__init__(self)
	
	def sput(self, data):
		self.squeue.put( { 'type': self.type, 'data': data, 'client': self } )
		
	def rput(self, data):
		self.rqueue.put( { 'type': self.type, 'data': data, 'client': self } )