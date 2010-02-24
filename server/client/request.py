##
# request.py
##

from log.logger import Log

class Request(object):
	def __init__(self):
		self.__header = {}
		self.__post = {}
		self.__get = {}
		self.path = None
		self.method = None
		self.protocol = None

	def handle(self, data):
		"""
		Traite une requete HTTP sur le server.
		Le header est parse, les variables en get et en post
		"""
		
		request_lines = data.replace('\r', '').split('\n')
		for line in request_lines:
			head_key = line.split(' ')[0].replace(':', '').lower()
			if len(head_key) > 0:
				if head_key == 'get' or head_key == 'post':
					self.method = head_key
				self.__header[head_key] = line[len(head_key) + 1:].strip()
				if self.method == 'post' and len(line.split(' ')) == 1:
					self.__handle_POST(line)
		self.__handle_METHOD()
	
	#
	def header_DATA(self, key):
		"""
		Recupere les donnees contenus dans le header de la requete
		get, host, connection, user-agent, cache-control, accept,
		accept-encoding, accept-language, accept-charset
		"""
		
		try:
			return self.__header[key.lower()]
		except KeyError:
			Log().add("[-] Erreur dans la methode header_DATA, la key : " + key + " n'existe pas", "ired")
			return None
	
	def post_DATA(self, key):
		"""
		Recupere les donnees contenus dans le post de la requete
		"""
		
		try:
			return self.__post[key.lower()]
		except KeyError:
			Log().add("[-] Erreur dans la methode post_DATA, la key : " + key + " n'existe pas", "ired")
			return None
			
	def get_DATA(self, key):
		"""
		Recupere les donnees contenus dans le get de la requete
		"""
		
		try:
			return self.__get[key.lower()]
		except KeyError:
			Log().add("[-] Erreur dans la methode get_DATA, la key : " + key + " n'existe pas", "ired")
			return None

	def hasPost(self):
		return len(self.__post) > 0
			
	def __handle_POST(self, post):
		"""
		Parse une requete post et la transforme en un objet [key]=value
		"""
		
		post_data = post.split('&')
		for data in post_data:
			try:
				(var_name, var_content) = data.split('=')
				self.__post[var_name.lower()] = var_content
			except ValueError:
				Log().add("[-] Erreur dans la methode __handle_POST data : " + data, "ired")
			
	def __handle_METHOD(self):
		"""
		Recupere la version du protocol HTML et le path de la requete
		"""
		
		if self.method:
			line = self.header_DATA(self.method)
			(self.path, self.protocol) = line.split(' ')
			self.__handle_PATH_DATA()
	
	def __handle_PATH_DATA(self):
		"""
		Recupere les donnees contenues dans le chemin de la requete GET/POST
		"""
		
		if self.path:
			index = self.path.find('?') or self.path.find('&')
			path_data = self.path[index + 1:].replace('/', '').split('&')
			for data in path_data:
				try:
					(var_name, var_content) = data.split('=')
					self.__get[var_name.lower()] = var_content
				except ValueError:
					Log().add("[-] Erreur dans la methode __handle_PATH_DATA data : " + data, "ired")