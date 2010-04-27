from twisted.internet.task import deferLater
from twisted.web.server import NOT_DONE_YET
from twisted.internet import reactor, defer
from twisted.web import resource
from log.logger import Log
from config.settings import SETTINGS
from commons.approval import Approval
from commons.session import Session

class ClientHTTP(resource.Resource):
	isLeaf = True

	def getData(self, uid):
		client = Session().get(uid)
		if client is None:
			return ''
		responses = client.getResponse()
		json = ''
		for res in responses:
			if '{"from": "connected",' not in res:
				json += (res + "\n")
		return json

	def render_POST(self, request):
		if request.args.get('json', None) is not None:
			uid = Approval().validate(request.args['json'][0])
			if '{"cmd": "connected", "args": "null"}' in request.args['json'][0]:
				return '{"from": "connected", "value": "%s"}' % uid
			return self.getData(uid)
		return '{"from": "error", "value": "No JSON key"}'
