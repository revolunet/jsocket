/**
 * Javascript event's interface for flash swf socket bridge
 */
var jsocketCoreHTTP = {
	api : null,
	initialized : false,
	connectedToServer : false,
	url : '',

	/**
	* Initialisation du core HTTP
	* @void
	**/
	loaded : function()
	{
		jsocketCoreHTTP.initialized = true;
		jsocketCoreHTTP.connectedToServer = false;
		jsocketCoreHTTP.socket = null;
		jsocketCoreHTTP.url = jsocketCoreHTTP.api.host;
		return (true);
	},

	/**
	* Permet d'effectuer une requete HTTP POST sur le serveur (host, port)
	* @parameters : {"cmd": "toto", "app": "tata", "channel": "titi"}
	**/
	_post : function(parameters)
	{
		jsocketCoreHTTP.socket = false;
		parameters = encodeURI('?json=' + parameters);
		if (window.XMLHttpRequest) {
			jsocketCoreHTTP.socket = new XMLHttpRequest();
			if (jsocketCoreHTTP.socket.overrideMimeType) {
				http_request.overrideMimeType('text/html');
			}
		}
		else if (window.ActiveXObject) {
			try {
				http_request = new ActiveXObject("Msxml2.XMLHTTP");
			}
			catch (e) {
				try {
					http_request = new ActiveXObject("Microsoft.XMLHTTP");
				}
				catch (e) { }
			}
		}
		if (!jsocketCoreHTTP.socket) {
			alert('Cannot create XMLHTTP instance');
			return (false);
		}
		jsocketCoreHTTP.socket.onreadystatechange = jsocketCoreHTTP.receive;
		jsocketCoreHTTP.socket.open('POST', jsocketCoreHTTP.url, true);
		jsocketCoreHTTP.socket.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		jsocketCoreHTTP.socket.setRequestHeader("Content-length", parameters.length);
		jsocketCoreHTTP.socket.setRequestHeader("Connection", "close");
		jsocketCoreHTTP.socket.send(parameters);
		return (true);
	},
 
	/**
	* Initialise une connection via une socket sur le server:port
	* @server : Hostname ou adresse IP du serveur
	* @port : Numero du port du serveur
	**/
	connect : function(server, port)
	{
		if (jsocketCoreHTTP.initialized == true && jsocketCoreHTTP.connectedToServer == false) {
			jsocketCoreHTTP.socket.connect(server, port);
		}
		else if (jsocketCoreHTTP.connectedToServer == false) {
			setTimeout("jsocketCoreHTTP.reconnect();", 500);
		}
	},
 
	/**
	* Alias de connect sans avoir a repreciser les parametres de connection
	* @void
	**/
	reconnect : function()
	{
		jsocketCoreHTTP.connect(jsocketCoreHTTP.api.host, jsocketCoreHTTP.api.port);
	},

	/**
	* Addslashes les caracteres ' " \\ \0
	* @str : Texte a addslasher
	**/
	addslashes : function(str)
	{
		if (typeof(str) == 'string') {
			str = encodeURIComponent(str);
			str = str.replace(/'/g, "%27");
		}
		else if (typeof(str) == 'object') {
			for (var i in str) {
				str[i] = jsocketCoreHTTP.addslashes(str[i]);
			}
		}
		return (str);
	},
 
	/**
	* Supprime tous les slashes des caracteres \' \" \\0 \\\\
	* @str : Texte a stripslasher
	**/
	stripslashes : function (str)
	{
		if (typeof(str) == 'string') {
			str = str.replace(/\%27/g, "'");
			str = decodeURIComponent(str);
		}
		else if (typeof(str) == 'object') {
			for (var i in str) {
				str[i] = jsocketCoreHTTP.stripslashes(str[i]);
			}
		}
		return (str);
	},

	/**
	* Envoie le message au serveur.
	* Tentative de reconnection a ce dernier le cas echeant.
	* @msg : Texte a envoyer au serveur
	**/
	write : function(msg)
	{
		jsocketCoreHTTP._post(msg + "\n");
		if (typeof jsocketCoreHTTP.api != 'object') {
			return (false);
		}
		setTimeout("jsocketCoreHTTP.send('" + msg + "');", 500);
		return (true);
	},
 
	/**
	* Alias de write
	* @msg : String a envoye au serveur
	**/
	send : function(msg)
	{
		return (jsocketCoreHTTP.write(msg));
	},
 
	/**
	* Callback appele par flash lorsque la socket est connectee au serveur
	* @void
	**/
	connected : function()
	{
		if (typeof jsocketCoreHTTP.api != 'object') {
			return (false);
		}
		jsocketCoreHTTP.connectedToServer = true;
		jsocketCoreHTTP.api.onReceive('{"from": "connect", "value": true}');
		return (true);
	},
 
	/**
	* Callback appele par flash lorsqu'une deconnection a ete effectuee
	* @void
	**/
	disconnected : function()
	{
		if (typeof jsocketCoreHTTP.api != 'object') {
			return (false);
		}
		jsocketCoreHTTP.api.parser('{"from": "disconnect", "value": true}');
		jsocketCoreHTTP.connectedToServer = false;
		jsocketCoreHTTP.reconnect();
		return (true);
	},
 
	/**
	* Callback appele par flash lorsqu'une Input/Output erreur survient
	* @msg : Message + Code d'erreur
	**/
	ioError: function(msg)
	{
		if (typeof jsocketCoreHTTP.api != 'object') {
			return (false);
		}
		jsocketCoreHTTP.api.parser('{"from": "error", "value": "' + msg + '"}');
		if (jsocketCoreHTTP.connectedToServer == false) {
			jsocketCoreHTTP.reconnect();
		}
		return (true);
	},
 
	/**
	* Callback appele par flash lorsqu'une erreur de securite survient
	* @msg : Message + Code d'erreur
	**/
	securityError: function(msg)
	{
		if (typeof jsocketCoreHTTP.api != 'object') {
			return (false);
		}
		jsocketCoreHTTP.api.parser('{"from": "error", "value": "' + msg + '"}');
		if (jsocketCoreHTTP.connectedToServer == false) {
			jsocketCoreHTTP.reconnect();
		}
		return (true);
	},
 
	/**
	* Callback appele par socket lors de la reception d'un message
	**/
	receive: function()
	{
		if (typeof jsocketCoreHTTP.api != 'object') {
			return (false);
		}
		if (jsocketCoreHTTP.socket.readyState == 4) {
			if (jsocketCoreHTTP.socket.status == 200) {
				msg = jsocketCoreHTTP.socket.responseText;
				jsocketCoreHTTP.connectedToServer = true;
				jsocketCoreHTTP.api.onReceive(msg);
			} else {
				jsocketCoreHTTP.api.parser('{"from": "error", "value": "No response from HTTP Server"}');
			}
		}
		setTimeout("jsocketCoreHTTP.receive();", 2000);
		return (true);
	}
};
