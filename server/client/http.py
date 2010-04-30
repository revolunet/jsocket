##
# http.py
##

from commons.validator import Validator
from log.logger import Log
from config.settings import SETTINGS
from server.watchdog import WatchDog
from commons.jexception import JException
from twisted.web import resource

class ClientHTTP(resource.Resource):
	isLeaf = True

	def render_POST(self, request):
		if request.args.get('json', None) is not None:
			Log().add('[+] HTTP Client received: %s' % (request.args['json'][0]))
			return request.args['json'][0]
		Log().add('[-] HTTP Client received no JSON key', 'red')
		return 'Bad request'
