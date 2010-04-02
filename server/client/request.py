##
# request.py
##

from log.logger import Log

class Request(object):
	"""
	Handle sur une request de type HTTP.
	Cette class va segmente la requete afin de la transformer en un objet facilement utilisable.
	"""
	
	def __init__(self):
		"""
		Request Constructeur :
			__header: les header de la requete, sous forme de [key] = value
			__post: les data postes sur le server, sous forme de [key] = value
			__get: les data contenues en get lors de la request sur le server, sous la fome de [KEY] = value
			__blackList: liste de mot clef a ignorer lors d'une requete, sous la forme d'une liste de mot clef.
			path: chemin de la requete.
			method: post/get..
			protocol: HTTP/1.1 ...
		"""
		
		self.__header = {}
		self.__post = {}
		self.__get = {}
		self.path = None
		self.method = None
		self.protocol = None
		self.__blackList = []
		self.__BlackList()
	
	def __BlackList(self):
		"""
		Liste de mots clef a ignorer lors d une requete.
		"""
		
		self.__blackList.append("favicon.ico")

	def handle(self, data):
		"""
		Traite une requete HTTP sur le server.
		Le header est parse, les variables en get et en post
		"""

		request_lines = data.replace('\r', '').split('\n')
		for line in request_lines:
			head_key = line.split(' ')[0].replace(':', '').lower()
			if len(head_key) > 0:
				if head_key == 'get' or head_key == 'post' or head_key == 'options':
					self.method = head_key
				self.__header[head_key] = line[len(head_key) + 1:].strip()
				if self.method == 'post' and len(line.split(' ')) == 1:
					self.__handle_POST(line)
		self.__handle_METHOD()
	
	def header_DATA(self, key):
		"""
		Recupere les donnees contenus dans le header de la requete
		get, host, connection, user-agent, cache-control, accept,
		accept-encoding, accept-language, accept-charset...
		"""
		
		try:
			return self.__header[key.lower()]
		except KeyError:
			Log().add("[-] Erreur dans la methode header_DATA, la key : " + key + " n'existe pas", "ired")
			return None
	
	def post_Ket_Exists(self, key):
		"""
		Verifie que la key existe dans le dictionnaire POST
		"""
		
		if len(key) == 0:
			return False
		return key.lower() in self.__post
	
	def post_DATA(self, key = None):
		"""
		Recupere les donnees contenus dans le post de la requete
		"""
		
		if key is not None:
			try:
				return self.__post[key.lower()]
			except KeyError:
				Log().add("[-] Erreur dans la methode post_DATA, la key : " + key + " n'existe pas", "ired")
				return None
		return self.__post
			
	def get_DATA(self, key = None):
		"""
		Recupere les donnees contenus dans le get de la requete
		"""
		
		if key is not None:
			try:
				return self.__get[key.lower()]
			except KeyError:
				Log().add("[-] Erreur dans la methode get_DATA, la key : " + key + " n'existe pas", "ired")
				return None
		return self.__get

	def hasPost(self):
		"""
		Return: Si des datas ont etes postes ou non -> bool
		"""
		
		return len(self.__post) > 0
			
	def __handle_POST(self, post):
		"""
		Parse une requete post et la transforme en un objet [key]=value
		"""

		post_data = post.replace('?', '')
		post_data = post_data.split('&')
		for data in post_data:
			try:
				if len(data):
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
					if data in self.__blackList:
						return
					if len(data):
						(var_name, var_content) = data.split('=')
						self.__get[var_name.lower()] = var_content
				except ValueError:
					Log().add("[-] Erreur dans la methode __handle_PATH_DATA data : " + data, "ired")