##
# http.py
##

from client.iClient import IClient
from log.logger import Log
from config.settings import SETTINGS
from request import Request
from response import Response
from server.watchdog import WatchDog
from commons.jexception import JException
import simplejson
import urllib
import time

def profileitdd(printlines=20):
	def _my(func):
		def _func(*args, **kargs):
			import hotshot, hotshot.stats
			prof = hotshot.Profile("profiling.data")
			res = prof.runcall(func, *args, **kargs)
			prof.close()
			stats = hotshot.stats.load("profiling.data")
			stats.strip_dirs()
			stats.sort_stats('time', 'calls')
			print ">>>---- Begin profiling print"
			stats.print_stats(printlines)
			print ">>>---- End profiling print"
			return res 
		return _func
	return _my

##
# Handle HTTP Client WEBRequests
##
class ClientHTTP(IClient):
	def __init__(self, client_socket, client_address, room, rqueue, squeue, http_list, session):
		self.client_socket = client_socket
		self.client_address = client_address
		self.request = Request()
		self.response = Response()
		self.validJson = False
		self.isUrlLib = False
		IClient.__init__(self, room, rqueue, squeue, 'http', http_list, session)
	
	def get_name(self):
		"""Return : Si l utilisateur n a pas de nickname on retourne la unique_key sinon son nickmae -> string """
		
		if self.nickName == None:
			return self.unique_key
		return self.nickName
	
	def sockRead(self):
		try:
			data = buffer = self.client_socket.recv(SETTINGS.SERVER_MAX_READ).strip()
			while len(buffer) == SETTINGS.SERVER_MAX_READ:
				buffer = self.client_socket.recv(SETTINGS.SERVER_MAX_READ).strip()
				data = data + buffer
			return data
		except:
			self.client_socket = None
			self.disconnection()
		return None

	#@profileitdd(40)
	def run(self):
		"""lecture du client """
		
		try:
			data = self.sockRead()
			if data is not None:
				self.request.handle(data)
				protocol = self.request.protocol
			
				if self.request.header_DATA('expect') is not None:
					buff = self.response.Get(self.request, 100)
					self.client_socket.send(buff)
					data = self.sockRead()
					if data is not None:
						self.request.handle(data)
				
				#urllib
				if self.request.hasPost():
					pass
				elif self.request.header_DATA('connection') is not None and self.request.header_DATA('connection') == 'close':
					self.isUrlLib = True
					self.response.AddHeader('connection', 'close')
					buff = self.response.Get(self.request, 200)
					self.client_socket.send(buff)
					data = self.sockRead()
					if data is not None:
						self.request.handle(data)
				elif self.request.hasPost() == False:
					pass
				elif self.request.header_DATA('User-Agent') is not None and self.request.header_DATA('User-Agent') == 'Python-urllib/2.5':
					self.isUrlLib = True
					self.response.AddHeader('connection', 'close')
					buff = self.response.Get(self.request, 200)
					self.client_socket.send(buff)
					data = self.sockRead()
					if data is not None:
						self.request.handle(data)

				if self.request.post_DATA('json') is not None:
					if len(self.request.post_DATA('json')) != 0:
						#try:
							json_data = urllib.unquote_plus(self.request.post_DATA('json')).split('\n')
							for data in json_data:
								data = data.strip()
								if len(data) > 0:
									try:
										json_cmd = simplejson.loads(data)
										json_uid = json_cmd.get('uid', None)
										if self.isUrlLib:
											self.response = Response()
										if json_cmd['cmd'] == 'connected':
											self.validJson = True
											self.setSession(self.unique_key)
											rep = '{"from": "connected", "value": "'+self.unique_key+'", "app": ""}'
											if self.isUrlLib:
												self.client_socket.send(self.response.GetUrlLib(protocol, 200, rep))
											else:
												self.client_socket.send(rep)
											self.disconnection()
										elif json_cmd['cmd'] == 'refresh':
											self.validJson = True
											if json_uid is None:
												self.client_socket.send('{"form": "error", "value": "No uid given"')
											else:
												try:
													clientSession = self.session.get(json_uid)
													if clientSession is not None:
														clientSession['last_action'] = int(time.time())
														self.last_action = int(time.time())
														self.session.updateSessionDic(json_uid, clientSession)
														#self.session.update(json_uid, clientSession)
												except KeyboardInterrupt:
													raise
												except:
													Log().add(JException().formatExceptionInfo())
												if json_uid is not None and self.http_list.get(json_cmd.get('uid'), None) is not None:
													if self.isUrlLib:
														self.client_socket.send(protocol + " 200 0K\r\n")
													for s in self.http_list.get(json_cmd.get('uid')):
														if len(s) > 0:
															self.client_socket.send(s + '\n')
													self.http_list[json_cmd['uid']] = [ ]
											self.disconnection()
										else:
											if json_uid is None:
												s = '{"form": "error", "value": "No uid given"'
												if self.isUrlLib:
													self.client_socket.send(self.response.GetUrlLib(protocol, 200, s))
												else:
													self.client_socket.send(s)
												self.disconnection()
											else:
												self.restoreSession(json_uid)
												self.validJson = True
												self.rput(data)
									except KeyboardInterrupt:
										raise
									except Exception:
										Log().add("[-] JSON error with simplejson.loads(data) data: %s" % data)
										if self.client_socket is not None:
											self.client_socket.send(protocol + " 200 0K\r\n")
										self.disconnection()
						#except Exception:
						#	Log().add(JException().formatExceptionInfo())
						#	self.disconnection() # NOT SURE !
				else:
					Log().add("[-] HTTP Request, no json data BYE ! ", 'red')
					self.disconnection()
		except KeyboardInterrupt:
			raise
		except Exception as e:
			Log().add(JException().formatExceptionInfo())
			self.disconnection()
			return
		self.disconnection()
		return
	
	# outdated
	def handleMethod(self):
		"""Si la methode utilise dans la requette HTTP est de type option on ne fait rien, sinon on ajoute a rqueue le json."""
		
		if self.request.method == 'options':
			pass
		else:
			if self.request.post_Ket_Exists("json") and len(self.request.post_DATA("json")) > 0:
				self.rqueue.put([self, urllib.unquote_plus(self.request.post_DATA("json"))])
	
	def queue_cmd(self, command):
		"""Ajoute une commande a la Queue en cours"""
		
		self.sput(command)
	
	def disconnection(self):
		"""On ferme la socket serveur du client lorsque celui-ci a ferme sa socket cliente"""
		
		if self.client_socket is not None:
			self.client_socket.close()
			self.client_socket = None
			Log().add("[-] HTTP Client disconnected", 'blue')
