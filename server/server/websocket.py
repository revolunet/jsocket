# coding: utf-8
# (c) 2009 Gleicon Moraes
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory
import re

class BasicOperations(object):
	"""
	Basic twisted websockets operations handler. Overwrite it with your operations.
	"""

	def __init__(self):
		self.writeHandler = None

	def on_read(self, sendLine):
		pass

	def on_connect(self):
		pass

	def on_close(self, r):
		pass

	def setWriteHandler(self, handler):
		self.writeHandler = handler

	def send(self, msg):
		if self.writeHandler == None:
			print 'No handler'
		else:
			self.writeHandler('\x00%s' % msg.encode('utf-8'))

	def after_connection(self):
		pass

class WebSocketServer(LineReceiver):
	HDR_ORIGIN = re.compile('Origin\:\s+(.*)')
	HDR_LOCATION = re.compile('GET\s+(.*)\s+HTTP\/1.1', re.I)
	HDR_HOST = re.compile('Host\:\s+(.*)')

	def __init__(self):
		self.hdr = '''HTTP/1.1 101 Web Socket Protocol Handshake\r
Upgrade: WebSocket\r
Connection: Upgrade\r
WebSocket-Origin: %s\r
WebSocket-Location: ws://%s%s\r\n\r\n'''

	def connectionMade(self):
		self.setRawMode()
		self.factory.oper.on_connect()

	def lineReceived(self, line):
		self.factory.oper.on_read(line[1:].decode('utf-8', 'ignore'))

	def rawDataReceived(self, line):
		origin, location, host = self._parseHeaders(line)
		self.sendLine(self.hdr % (origin, host, location))
		self.delimiter = '\xff'
		self.setLineMode()
		self.factory.oper.setWriteHandler(self.sendLine)
		self.factory.oper.after_connection()

	def connectionLost(self, reason):
		self.factory.oper.on_close(reason)

	def _parseHeaders(self, buf):
		o = None
		l = None
		h = None
		for a in buf.split('\n\r'):
			org = self.HDR_ORIGIN.search(a)
			loc = self.HDR_LOCATION.search(a)
			hst = self.HDR_HOST.search(a)
			if org != None:
				o = org.group(1).strip()
			if hst != None:
				h = hst.group(1).strip()
			if loc != None:
				l = loc.group(1).strip()
		return o, l, h

class WebSocketFactory(Factory):
	protocol = WebSocketServer

	def __init__(self, oper = BasicOperations):
		self.oper = oper
