##
# http.py
##

import simplejson
from log.logger import Log
from config.settings import SETTINGS
from server.watchdog import WatchDog
from commons.jexception import JException
from twisted.web import resource

def clientHTTP(environ, start_response):
	Log().add('[HTTPDEBUG] environ: "%s"' % str(environ))
	status = '200 OK'
	output = 'Pong!'
	response_headers = [('Content-type', 'text/plain'),
						('Content-Length', str(len(output)))]
	start_response(status, response_headers)
	return [output]

class ClientHTTP(resource.Resource):
	isLeaf = True
	def render_POST(self, request):
		if request.args.get('json', None) is not None:
			Log().add('[+] HTTP Client received: %s' % (request.args['json'][0]))
			return request.args['json'][0]
		Log().add('[-] HTTP Client received no JSON key', 'red')
		return 'Bad request'
