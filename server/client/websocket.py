import datetime

from server.websocket import WebSocketHandler
from commons.approval import Approval
from log.logger import Log

class ClientWebSocket(WebSocketHandler):
	"""
	Classe WebSocket HTML5 utilisee par twisted
	"""

	def callbackSend(self, responses):
		""" Callback appele par le :func:`WorkerParser` lorsque des reponses sont pretes """
		for json in responses:
			if '{"from": "connected",' not in json:
				self.transport.write(json)

	def frameReceived(self, frame):
		""" Methode appelee lorsque l'utilisateur recoit des donnees """
		Log().add('[WebSocket] Received: %s' % frame)
		commands = frame.split("\n")
		for cmd in commands:
			if '{"cmd": "connected", "args": "null"' in cmd:
				uid = Approval().validate(cmd)
				self.transport.write('{"from": "connected", "value": "%s"}' % uid)
			else:
				Approval().validate(cmd, self.callbackSend)
