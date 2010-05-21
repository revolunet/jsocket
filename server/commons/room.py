##
# room.py
##

from config.settings import SETTINGS
from commons.application import Application

class Room(object):
	def __init__(self):
		self.applications = {}
		self.init_app()
		
	def init_app(self):
		for app in SETTINGS.STARTUP_APP:
			self.applications[app] = Application(app)
		
	def list_users(self, appName = None):
		if appName in self.applications:
			return self.applications[appName].users()
		return []
		
	def create(self, appName, uid, password = None):
		if appName in self.applications:
			import random
			app = Application(appName)
			app.master_password = random.getrandbits(16)
			app.add(uid, app.master_password)
			if password is not None:
				app.password = password
			self.applications[appName] = app
			return True
		return False
		
	def remove(self, appName):
		if appName in self.applications:
			self.applications.pop(appName)
			return True
		return False
		
	def join(self, appName, uid, password = None):
		if appName in self.applications:
			if password is not None:
				if self.applications[appName].password == password:
					self.applications[appName].add(uid)
				else:
					return False
			else:
				self.applications[appName].add(uid)
			return True
		return False
	
	def part(self, appName, uid):
		if appName in self.applications:
			self.applications[appName].delete(uid)
			return True
		return False
		
	def Application(self, appName):
		if appName in self.applications:
			return self.applications[appName]
		return None
		
	def forward(self, appName, commande, uid, app):
		from commons.session import Session
		
		if appName in self.applications and uid in self.applications[appName].masters:
			users = self.applications[appName].users()
			master = Session().get(uid)
			json = Protocol.forgeJSON('forward', '["' + master.getName() + '", "' + commande + '"]',
												  {'channel': appName, 'app': app})
			for u in users:
				user = Session().get(u)
				user.addResponse(json)
			if len(users) > 1:
				return True
		return False
		
	def message(self, appName, sender, users, message, app):
		if appName in self.applications:
			if len(users) > 0:
				if users[0] == 'master' and sender in self.applications[appName].masters():
					masters = self.applications[appName].masters()
					for master in masters:
						self.__sendMessage(appName, sender, master, message, app)
					return True
				list_users = self.applications[appName].users()
				if len(list_users) >= 1:
					if users[0] == 'all':
						for u in list_users:
							self.__sendMessage(appName, sender, u, message, app)
						return True
					for user in list_users:
						if user in users:
							self.__sendMessage(appName, sender, user, message, app)
					return True
		return False
		
	def appAuth(self, appName, password, uid):
		
		if appName in self.applications:
			return self.applications[appName].add(uid, password)
		return False
	
	def changeAppMasterPwd(self, appName, password):
		
		if appName in self.applications:
			self.applications[appName].master_password = password
			return True
		return False
				
	def appExists(self, appName):
		return appName in self.applications
		
	def __sendMessage(self, appName, sender, to, message, app):
		from commons.session import Session
		
		sender = Session().get(sender)
		receiver =  Session().get(to)
		json = Protocol.forgeJSON('message', '["' + sender.getName() + '", "' + message + '"]',
											  {'channel': channelName, 'app': app})
		receiver.addResponse(json)