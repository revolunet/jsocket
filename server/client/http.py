from twisted.internet.task import deferLater
from twisted.web.server import NOT_DONE_YET
from twisted.internet import reactor, defer
from twisted.web import resource
from log.logger import Log
from config.settings import SETTINGS
from commons.approval import Approval
from commons.session import Session

"""
from twisted.internet.task import deferLater
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from twisted.internet import reactor

class DelayedResource(Resource):
	def _delayedRender(self, request):
		request.write("Sorry to keep you waiting.")
		request.finish()

	def render_GET(self, request):
		d = deferLater(reactor, 5, lambda: request)
		d.addCallback(self._delayedRender)
		return NOT_DONE_YET

resource = DelayedResource()
"""

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
		Log().add('!JSON!: %s' % json)
		return json

	def render_POST(self, request):
		Log().add('ENTER IN POST\n\n')
		if request.args.get('json', None) is not None:
			Log().add('[+] HTTP Client received: %s' % (request.args['json'][0]))
			uid = Approval().validate(request.args['json'][0])
			Log().add('[!] HTTP Client uid: %s' % uid)
			if '{"cmd": "connected", "args": "null"}' in request.args['json'][0]:
				return '{"from": "connected", "value": "%s"}' % uid
			return self.getData(uid)
		Log().add('[-] HTTP Client received no JSON key', 'red')
		return '{"from": "error", "value": "No JSON key"}'
