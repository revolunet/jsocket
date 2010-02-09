##
# client.py
##

import threading
import json
import random
from log import Log

class Client(threading.Thread):
	def __init__(self, client_socket, client_address, room, rqueue, squeue):
		self.client_socket = client_socket
		self.client_address = client_address
		self.master = True
		self.__room = room
		self.__master_password = "admin"
		self.__init_cmd()
		self.__unique_key = hex(random.getrandbits(64))
		self.__rqueue = rqueue
		self.__squeue = squeue
		self.__room_name = None
		threading.Thread.__init__(self)
		
	def __init_cmd(self):
		"""On initialise la liste des commandes disponnible"""

		self.__cmd_list = {
			'create' : self.__cmd_create,
			'join' : self.__cmd_join,
			'part' : self.__cmd_part,
			'auth' : self.__cmd_auth,
			'delete' : self.__cmd_delete
		}
	
	def run(self):
		"""Boucle de lecture du client"""
		
		self.__connected()
		while 1:
			data = self.client_socket.recv(1024).strip()
			if len(data) == 0:
				self.__disconnection()
				return
			else:
				self.__rqueue.put([self, data])
				Log().add("[+] Client " + str(self.client_address) + " send : " + data)
	
	def __connected(self):
		"""Le client est connecte, sa cle unique lui est send"""
		
		self.__squeue.put([self, self.__unique_key])
		
	def parse(self, cmd):
		"""Parsing de l'entre json sur le serveur"""
		
		try:
			json_cmd = json.loads(cmd)
			if json_cmd['cmd'] and json_cmd['cmd'] in self.__cmd_list:
				try :
					if json_cmd['args']:
						self.__cmd_list [json_cmd['cmd']](json_cmd['args'])
				except KeyError:
					Log().add("[+] Command error : " + cmd + " , '" + json_cmd['cmd'] + "' prends deux arguments", 'ired')
			else:
				Log().add("[+] Command error : " + cmd + " , '" + json_cmd['cmd'] + "' n'est pas une commande valide", 'yellow')
		except ValueError:
			Log().add("[+] Command error : " + cmd + " , n'est pas une chaine json valide", 'ired')
	
	# {"cmd": "delete", "args": "irc"}
	def __cmd_delete(self, args):
		"""On supprimet un channel, si celui si existe et que Client est Master"""
		
		if self.master and self.__room.delete(args):
			self.__squeue.put([self, "True"])
			Log().add("[+] Le channel " + args + " a ete supprime par : " + str(self.client_address))
		else:
			if self.master:
				Log().add("[+] Command error : la commande delete a echoue ( le channel " + args + " n'existe pas )", 'yellow')
			else:
				Log().add("[+] Command error : la commande delete a echoue ( le Client n'est pas master )", 'yellow')
			self.__squeue.put([self, "False"])
			
	# {"cmd": "create", "args": "irc"}
	def __cmd_create(self, args):
		"""Creation d'un nouveau channel si le Client est Master"""
		
		if self.master and self.__room.create(args):
			Log().add("[+] Un nouveau channel a ete ajoute par : " + str(self.client_address))
			self.__squeue.put([self, "True"])
		else:
			if self.master:
				Log().add("[+] Command error : la commande create a echoue ( le channel existe deja )", 'yellow')
			else:
				Log().add("[+] Command error : la commande create a echoue ( le Client n'est pas master )", 'yellow')
			self.__squeue.put([self, "False"])

	# {"cmd": "join", "args": "irc"}
	def __cmd_join(self, args):
		"""Ajoute un client dans le salon specifie"""
		
		if self.__room.join(args, self):
			self.__room_name = args
			Log().add("[+] Client : l'utilisateur " + str(self.client_address) + " a rejoin le channel : " + args, 'yellow')
			self.__squeue.put([self, "True"])
		else:
			Log().add("[+] Command error : le channel " + args + " n'existe pas ", 'yellow')
			self.__squeue.put([self, "False"])
			
	
	# {"cmd": "part", "args": "irc"}
	def __cmd_part(self, args):
		"""Supprime un client du salon specifie"""
		
		if self.__room_name and self.__room.part(self.__room_name, self):
			self.__room_name = None
			Log().add("[+] Client : le client " + str(self.client_address) + " a quitte le channel : " + args)
			self.__squeue.put([self, "True"])
		else:
			Log().add("Command error : l'utilisateur n'est pas dans le channel : " + args)
			self.__squeue.put([self, "False"])
	
	# {"cmd": "auth", "args": "passphrase"}
	def __cmd_auth(self, args):
		"""Auth pour definir si le Client est desormais master ou non"""
		
		if args == self.__master_password:
			self.master = True
			Log().add("[+] Client : le client " + str(self.client_address) + " est a present master sur le serveur")
			self.__squeue.put([self, "True"])
		else:
			self.__squeue.put([self, "False"])
				
	def __disconnection(self):
		"""On ferme la socket serveur du client lorsque celui-ci a ferme sa socket cliente"""

		if self.__room_name:
			self.__room.part(self.__room_name, self)			
		self.client_socket.close()
		Log().add("[-] Client disconnected", 'blue')
