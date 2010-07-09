/**
 * @class SocketBridge
 */
class SocketBridge {
  /**
   * @var {flash.net.Socket} socket
   */
  static var socket : flash.net.Socket = new flash.net.Socket();

  /**
   * @var {Object} jsScope
   */
  static var jsScope : String = "";

  /**
   * @var {flash.utils.ByteArray} buffer
   */
  static var buffer : flash.utils.ByteArray = new flash.utils.ByteArray();

  /**
   * @method main
   */
  static function main() {
	/**
	 * Security settings
	 */
	flash.system.Security.allowDomain("*");

	if (flash.external.ExternalInterface.available) {
	  jsScope = flash.Lib.current.loaderInfo.parameters.scope;
	  if (jsScope == null) {
		jsScope = "";
	  } else {
		jsScope += ".";
	  }

	  /**
	   * Calls the javascript load method once the SWF has loaded
	   */
	  flash.external.ExternalInterface.call("setTimeout", jsScope + "loaded()");

	  /**
	   * Set event listeners for socket
	   * @event
	   * Connect
	   */
	  socket.addEventListener(flash.events.Event.CONNECT, function(e) : Void {
		  trace("[+] Connected to server.");
		  flash.external.ExternalInterface.call("setTimeout", jsScope + "connected()", 0);
	  });

	  /**
	   * @event
	   * Close
	   */
	  socket.addEventListener(flash.events.Event.CLOSE, function(e) : Void {
		  trace("[-] Disconnected from server.");
		  flash.external.ExternalInterface.call("setTimeout", jsScope + "disconnected()", 0);
	  });

	  /**
	   * @event
	   * IO Error
	   */
	  socket.addEventListener(flash.events.IOErrorEvent.IO_ERROR, function(e) : Void {
		  trace("[!] IOERROR : " +  e.text);
		  flash.external.ExternalInterface.call("setTimeout", jsScope + "ioError('" + e.text + "')" ,0);
	  });

	  /**
	   * @event
	   * Security Error
	   */
	  socket.addEventListener(flash.events.SecurityErrorEvent.SECURITY_ERROR, function(e) : Void {
		  trace("[!] SECURITY ERROR : " +  e.text);
		  flash.external.ExternalInterface.call("setTimeout", jsScope + "securityError('" +e.text+ "')", 0);
	  });

	  /**
	   * @event
	   * Socket Data
	   */
	  socket.addEventListener(flash.events.ProgressEvent.SOCKET_DATA, function(e) : Void {
		  var pos : Int = buffer.length;

		  socket.readBytes(buffer, pos);
		  while (pos < buffer.length) {
			if (buffer[pos] == 0xff && pos > 0) {
			  if (buffer[0] != 0x00) {
				trace("[!] Receive error: data must start with \\x00");
				return;
			  }
			  buffer.position = 1;
			  var data : String = buffer.readUTFBytes(pos - 1);
			  trace("[+] Received: " + data);
			  flash.external.ExternalInterface.call("setTimeout", jsScope + "receive('" + StringTools.urlEncode(data) + "')", 0);
			  removeBufferBefore(pos + 1);
			  pos = -1;
			}
			++pos;
		  }
	  });

	  /**
	   * Set External Interface Callbacks
	   */
	  flash.external.ExternalInterface.addCallback("connect", connect);
	  flash.external.ExternalInterface.addCallback("close", close);
	  flash.external.ExternalInterface.addCallback("write", write);
	}
	else {
	  trace("[!] Flash external interface not available.");
	}
  }

  /**
   * Connect to new socket server
   * @param {String} host The host the socket server resides on
   * @param {String} port The socket servers port
   */
  static function connect(host : String, port : String) {
	trace("[i] Connecting to socket server at " + host + ":" + port);
	socket.connect(host, Std.parseInt(port));
  }

  /**
   * Disconnect the socket
   */
  static function close() {
	if (socket.connected) {
	  trace("Closing current connection");
	  socket.close();
	} else {
	  trace("[!] Cannot disconnect to server because there is no connection.");
	}
  }

  /**
   * Write string to the socket
   * @param {String} msg Message to send to the socket
   */
  static function write(msg) {
	if (socket.connected) {
	  trace("Writing '" + msg + "' to server");
	  socket.writeByte(0x00);
      socket.writeUTFBytes(msg);
      socket.writeByte(0xff);
	  socket.flush();
	} else {
	  trace("[!] Cannot write to server because there is no connection.");
	}
  }

  /**
   * @method removeBufferBefore
   * @param {int} pos Current buffer position
   */
  static function removeBufferBefore(pos : Int) : Void {
	if (pos == 0) {
	  return;
	}
	var nextBuffer : flash.utils.ByteArray = new flash.utils.ByteArray();
	buffer.position = pos;
	buffer.readBytes(nextBuffer);
	buffer = nextBuffer;
  }
}
