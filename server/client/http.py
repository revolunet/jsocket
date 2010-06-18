from twisted.web import resource
from log.logger import Log
from config.settings import SETTINGS
from commons.approval import Approval
from commons.session import Session

class ClientHTTP(resource.Resource):
	"""
	Classe HTTP utilisee par twisted
	"""

	isLeaf = True

	def getData(self, uid):
		"""
		Recupere les reponses en suspend de l'utilisateur via son UID et
		les revoie separees par des \n
		"""

		client = Session().get(uid)
		if client is None:
			return ''
		responses = client.getResponse()
		json = ''
		for res in responses:
			if '{"from": "connected",' not in res:
				json += (res + "\n")
		if len(json) > 0:
			Log().add('[HTTP] Send: %s' % json)
		return json

	def render_POST(self, request):
		"""
		Traite les informations envoye par POST.
		Necessite la cle json.
		"""

		cuid = None
		if request.args.get('json', None) is not None:
			#if '{"cmd": "refresh", "args": "null",' not in request.args['json'][0]:
			Log().add('[HTTP] Receive: %s' % request.args['json'][0])
			commands = request.args['json'][0].split("\n")
			for cmd in commands:
				uid = Approval().validate(cmd)
				if uid is not None and cuid is None:
					cuid = uid
				if '{"cmd": "connected", "args": "null"' in request.args['json'][0]:
					return '{"from": "connected", "value": "%s"}' % cuid
			return self.getData(cuid)
		return '{"from": "error", "value": "No JSON key"}'
