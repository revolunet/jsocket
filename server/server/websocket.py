# Copyright (c) 2009 Twisted Matrix Laboratories.
# See LICENSE for details.

# Based on http://twistedmatrix.com/trac/browser/branches/websocket-4173-2/twisted/web/websocket.py

"""
WebSocket server protocol.

See U{http://tools.ietf.org/html/draft-hixie-thewebsocketprotocol} for the
current version of the specification.

@since: 10.1
"""

from twisted.web.http import datetimeToString
from twisted.web.server import Request, Site, version, unquote
import struct
import re
import hashlib


class WebSocketRequest(Request):
    """
    A general purpose L{Request} supporting connection upgrade for WebSocket.
    """
    handlerFactory = None

    def isWebSocket(self):
        return self.requestHeaders.getRawHeaders("Upgrade") == ["WebSocket"] and \
            self.requestHeaders.getRawHeaders("Connection") == ["Upgrade"]

    def process(self):
        if self.isWebSocket():
            return self.processWebSocket()
        else:
            return Request.process(self)


    def processWebSocket(self):
        """
        Process a specific web socket request.
        """
        # get site from channel
        self.site = self.channel.site

        # set an empty handler attribute
        self.handler = None

        # set various default headers
        self.setHeader("server", version)
        self.setHeader("date", datetimeToString())

        # Resource Identification
        self.prepath = []
        self.postpath = map(unquote, self.path[1:].split("/"))
        self.renderWebSocket()


    def _handshake75(self):
        origin  = self.requestHeaders.getRawHeaders("Origin",   [None])[0]
        host    = self.requestHeaders.getRawHeaders("Host",     [None])[0]
        if not origin or not host:
            return

        protocol = self.requestHeaders.getRawHeaders("WebSocket-Protocol", [None])[0]
        if protocol and protocol not in self.site.supportedProtocols:
            return

        if self.isSecure():
            scheme = "wss"
        else:
            scheme = "ws"
        location = "%s://%s%s" % (scheme, host, self.uri)
        handshake = [
            "HTTP/1.1 101 Web Socket Protocol Handshake",
            "Upgrade: WebSocket",
            "Connection: Upgrade",
            "WebSocket-Origin: %s" % origin,
            "WebSocket-Location: %s" % location,
            ]
        if protocol is not None:
            handshake.append("WebSocket-Protocol: %s" % protocol)

        return handshake

    def _handshake76(self):
        origin  = self.requestHeaders.getRawHeaders("Origin",   [None])[0]
        host    = self.requestHeaders.getRawHeaders("Host",     [None])[0]
        if not origin or not host:
            return None, None

        protocol = self.requestHeaders.getRawHeaders("Sec-WebSocket-Protocol", [None])[0]
        if protocol and protocol not in self.site.supportedProtocols:
            return None, None

        if self.isSecure():
            scheme = "wss"
        else:
            scheme = "ws"
        location = "%s://%s%s" % (scheme, host, self.uri)
        handshake = [
            "HTTP/1.1 101 Web Socket Protocol Handshake",
            "Upgrade: WebSocket",
            "Connection: Upgrade",
            "Sec-WebSocket-Origin: %s" % origin,
            "Sec-WebSocket-Location: %s" % location,
            ]
        if protocol is not None:
            handshake.append("Sec-WebSocket-Protocol: %s" % protocol)

        self.channel.setRawMode()

        # Refer to 5.2 4-9 of the draft 76
        key1 = self.requestHeaders.getRawHeaders('Sec-WebSocket-Key1', [None])[0]
        key2 = self.requestHeaders.getRawHeaders('Sec-WebSocket-Key2', [None])[0]
        key3 = self.content.getvalue()

        def extract_nums(s): return int(''.join(re.findall(r'[0-9]', s)))
        def count_spaces(s): return len(re.findall(r' ', s))
        part1 = extract_nums(key1) / count_spaces(key1)
        part2 = extract_nums(key2) / count_spaces(key2)
        challenge = hashlib.md5(struct.pack('>ii8s', part1, part2, key3)).digest()

        return handshake, challenge

    def gotLength(self, length):
        spec76 = self.requestHeaders.getRawHeaders("Sec-WebSocket-Key1", [None])[0]
        if self.isWebSocket() and spec76:
            self.channel.headerReceived("content-length: 8")
        Request.gotLength(self, length)

    def renderWebSocket(self):
        """
        Render a WebSocket request.

        If the request is not identified with a proper WebSocket handshake, the
        connection will be closed. Otherwise, the response to the handshake is
        sent and a C{WebSocketHandler} is created to handle the request.
        """
        if self.queued:
            self.channel.transport.loseConnection()
            return

        if self.requestHeaders.getRawHeaders("Sec-WebSocket-Key1", [None])[0]:
            handshake, challenge_response = self._handshake76()
        else:
            handshake = self._handshake75()
            challenge_response = None

        if not handshake:
            self.channel.transport.loseConnection()
            return

        handlerFactory = self.site.handlers.get(self.uri) or self.handlerFactory
        if not handlerFactory:
            return self.channel.transport.loseConnection()
        transport = WebSocketTransport(self)
        handler = handlerFactory(transport)
        transport._attachHandler(handler)
        self.handler = handler

        self.startedWriting = True

        for header in handshake:
            self.write("%s\r\n" % header)

        self.write("\r\n")
        if challenge_response:
            self.write(challenge_response)

        self.channel.setRawMode()
        # XXX we probably don't want to set _transferDecoder
        self.channel._transferDecoder = WebSocketFrameDecoder(
            self, handler)
        return



class WebSocketSite(Site):
    """
    @ivar handlers: a C{dict} of names to L{WebSocketHandler} factories.
    @type handlers: C{dict}
    @ivar supportedProtocols: a C{list} of supported I{WebSocket-Protocol}
        values. If a value is passed at handshake and doesn't figure in this
        list, the connection is closed.
    @type supportedProtocols: C{list}
    """
    requestFactory = WebSocketRequest

    def __init__(self, resource, logPath=None, timeout=60*60*12,
                 supportedProtocols=None):
        Site.__init__(self, resource, logPath, timeout)
        self.handlers = {}
        self.supportedProtocols = supportedProtocols or []


    def addHandler(self, name, handlerFactory):
        """
        Add or override a handler for the given C{name}.

        @param name: the resource name to be handled.
        @type name: C{str}
        @param handlerFactory: a C{WebSocketHandler} factory.
        @type handlerFactory: C{callable}
        """
        if not name.startswith("/"):
            raise ValueError("Invalid resource name.")
        self.handlers[name] = handlerFactory



class WebSocketTransport(object):
    """
    Transport abstraction over WebSocket, providing classic Twisted methods and
    callbacks.
    """
    _handler = None

    def __init__(self, request):
        self._request = request
        self._request.notifyFinish().addErrback(self._connectionLost)


    def _attachHandler(self, handler):
        """
        Attach the given L{WebSocketHandler} to this transport.
        """
        self._handler = handler


    def _connectionLost(self, reason):
        """
        Forward connection lost event to the L{WebSocketHandler}.
        """
        self._handler.connectionLost(reason)


    def write(self, frame):
        """
        Send the given frame to the connected client.

        @param frame: a I{UTF-8} encoded C{str} to send to the client.
        @type frame: C{str}
        """
        self._request.write("\x00%s\xff" % frame)


    def loseConnection(self):
        """
        Close the connection.
        """
        self._request.transport.loseConnection()



class WebSocketHandler(object):
    """
    Base class for handling WebSocket connections. It mainly provides a
    transport to send frames, and a callback called when frame are received,
    C{frameReceived}.

    @ivar transport: a C{WebSocketTransport} instance.
    @type: L{WebSocketTransport}
    """

    def __init__(self, transport):
        """
        Create the handler, with the given transport
        """
        self.transport = transport


    def frameReceived(self, frame):
        """
        Called when a frame is received.

        @param frame: a I{UTF-8} encoded C{str} sent by the client.
        @type frame: C{str}
        """


    def frameLengthExceeded(self):
        """
        Called when too big a frame is received. The default behavior is to
        close the connection, but it can be customized to do something else.
        """
        self.transport.loseConnection()


    def connectionLost(self, reason):
        """
        Callback called when the underlying transport has detected that the
        connection is closed.
        """



class WebSocketFrameDecoder(object):
    """
    Decode WebSocket frames and pass them to the attached C{WebSocketHandler}
    instance.

    @ivar MAX_LENGTH: maximum len of the frame allowed, before calling
        C{frameLengthExceeded} on the handler.
    @type MAX_LENGTH: C{int}
    @ivar request: C{Request} instance.
    @type request: L{twisted.web.server.Request}
    @ivar handler: L{WebSocketHandler} instance handling the request.
    @type handler: L{WebSocketHandler}
    @ivar _data: C{list} of C{str} buffering the received data.
    @type _data: C{list} of C{str}
    @ivar _currentFrameLength: length of the current handled frame, plus the
        additional leading byte.
    @type _currentFrameLength: C{int}
    """

    MAX_LENGTH = 16384


    def __init__(self, request, handler):
        self.request = request
        self.handler = handler
        self._data = []
        self._currentFrameLength = 0


    def dataReceived(self, data):
        """
        Parse data to read WebSocket frames.

        @param data: data received over the WebSocket connection.
        @type data: C{str}
        """
        if not data:
            return
        while True:
            endIndex = data.find("\xff")
            if endIndex != -1:
                self._currentFrameLength += endIndex
                if self._currentFrameLength > self.MAX_LENGTH:
                    self.handler.frameLengthExceeded()
                    break
                self._currentFrameLength = 0
                frame = "".join(self._data) + data[:endIndex]
                self._data[:] = []
                if frame[0] != "\x00":
                    self.request.transport.loseConnection()
                    break
                self.handler.frameReceived(frame[1:])
                data = data[endIndex + 1:]
                if not data:
                    break
                if data[0] != "\x00":
                    self.request.transport.loseConnection()
                    break
            else:
                self._currentFrameLength += len(data)
                if self._currentFrameLength > self.MAX_LENGTH + 1:
                    self.handler.frameLengthExceeded()
                else:
                    self._data.append(data)
                break



___all__ = ["WebSocketHandler", "WebSocketSite"]
