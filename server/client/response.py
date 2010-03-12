

from config.settings import SETTINGS
import datetime

class Response(object):
	"""docstring for Response"""
	def __init__(self):
		self.request = None
		self.http_version = "HTTP/1.0 "
		self.code = 200
		self.code_message = "OK"
		self.date = datetime.datetime.now() # GMT Server : Jsocket-Server/1.0
		#self.date.strftime("%a, %d %B %Y %H:%M:%S")
		self.content_type = "text/HTML"
		self.content_length = 0
		self.__code_status = { 	200: "OK",
								404: "NOT FOUND",
								403: "FORBIDDEN",
								401: "UNAUTHORIZED",
								500: "INTERNAL ERROR"
		}
		self.response_header = None
		self.response_data = None

	def HandleRequest(self, request):
		self.http_version = request.protocol
	
	def ResponseData(self, data):
		self.response_data = "\r\n"
		self.response_data += data
		self.response_data += "\r\n"
		self.content_length = len(data)
	
	def __createHeader(self, request):
		if request.protocol:
			self.response_header = str(request.protocol) + " " + str(self.code) + " " + str(self.__code_status[self.code]) + "\r\n"
		else:
			self.response_header = "HTTP/1.1 204 NO RESPONSE\r\n"
		self.response_header += "Date: " + str(self.date.strftime("%a, %d %B %Y %H:%M:%S")) + " " + SETTINGS.HTTP_SERVER_NAME +  "\r\n"
		self.response_header += "Content-Type: " + str(self.content_type) + "\r\n"
		
	def Get(self, request, code):
		self.code = code
		self.__createHeader(request)
		if self.response_data is not None:
			self.response_header += "Content-Length: " + str(self.content_length) + "\r\n"
			self.response_header += self.response_data
		return self.response_header