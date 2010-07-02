/**
 * @class SocketBridge
 */
class SocketBridge {
  static var socket = new flash.net.Socket();
  static var jsScope;

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
		  var i = 0;
		  var buffer = new flash.utils.ByteArray();
		  socket.readBytes(buffer, 0);
		  while (i < buffer.length) {
			if (buffer[i] == 0x00) {
			  var msg = buffer.readUTFBytes(i);
			  trace("Received: " + msg);
			  flash.external.ExternalInterface.call("setTimeout", jsScope + "receive('" + msg + "')", 0);
			  buffer.readByte();
			  var nextBuffer = new flash.utils.ByteArray();
			  buffer.readBytes(nextBuffer);
			  buffer = nextBuffer;
			  i = -1;
			}
			++i;
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
	  socket.writeUTFBytes("\x00" + msg + "\xff");
	  socket.flush();
	} else {
	  trace("[!] Cannot write to server because there is no connection.");
	}
  }
}
