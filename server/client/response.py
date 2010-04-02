

from config.settings import SETTINGS
import datetime

class Response(object):
	"""
	Formatage d'une reponse HTTP.
	Cet objet n'est pas utiliser par le server.
	"""
	
	def __init__(self):
		self.request = None
		self.http_version = "HTTP/1.0 "
		self.code = 200
		self.code_message = "OK"
		self.date = datetime.datetime.now() # GMT Server : Jsocket-Server/1.0
		#self.date.strftime("%a, %d %B %Y %H:%M:%S")
		self.content_type = "text/HTML"
		self.content_length = 0
		self.response_header = None
		self.response_data = None
		self.initHTTPCode()

	def HandleRequest(self, request):
		"""
		Recupere la version HTTP utilise par le client lors de la Request
		"""
		
		self.http_version = request.protocol
	
	def ResponseData(self, data):
		"""
		Set les datas renvoye au client apres une request
		"""
		
		self.response_data = "\r\n"
		self.response_data += data
		self.response_data += "\r\n"
		self.content_length = len(data)
	
	def __createHeader(self, request):
		"""
		Definie les headers de reponse a send au client.
		"""
		
		if request.protocol:
			self.response_header = str(request.protocol) + " " + str(self.code) + " " + str(self.__code_status[self.code]) + "\r\n"
		else:
			self.response_header = "HTTP/1.1 204 NO RESPONSE\r\n"
		self.response_header += "Date: " + str(self.date.strftime("%a, %d %B %Y %H:%M:%S")) + " " + SETTINGS.HTTP_SERVER_NAME +  "\r\n"
		self.response_header += "Content-Type: " + str(self.content_type) + "\r\n"
		
	def Get(self, request, code):
		"""
		Retourne le message associe a un code d'erreur -> string
		"""
		
		self.code = code
		self.__createHeader(request)
		if self.response_data is not None:
			self.response_header += "Content-Length: " + str(self.content_length) + "\r\n"
			self.response_header += self.response_data
		return self.response_header
	
	def initHTTPCode(self):
		"""
		Liste de tous les codes retour HTTP
		"""
		
		self.__code_status = {
			100: "Continue",
			101: "Switching Protocols",
			200: "OK",
			201: "Created",
			202: "Accepted",
			203: "Non-Authoritative Information",
			204: "No Content",
			205: "Reset Content",
			206: "Partial Content",
			300: "Multiple Choices",
			301: "Moved Permanently",
			302: "Found",
			303: "See Other",
			304: "Not Modified",
			305: "Use Proxy",
			307: "Temporary Redirect",
			400: "Bad Request",
			401: "Unauthorized",
			402: "Payment Required",
			403: "Forbidden",
			404: "Not Found",
			405: "Method Not Allowed",
			406: "Not Acceptable",
			407: "Proxy Authentication Required",
			408: "Request Timeout",
			409: "Conflict",
			410: "Gone",
			411: "Length Required",
			412: "Precondition Failed",
			413: "Request Entity Too Large",
			414: "Request-URI Too Long",
			415: "Unsupported Media Type",
			416: "Requested Range Not Satisfiable",
			417: "Expectation Failed",
			500: "Internal Server Error",
			501: "Not Implemented",
			502: "Bad Gateway",
			503: "Service Unavailable",
			504: "Gateway Timeout",
			505: "HTTP Version Not Supported",
		}