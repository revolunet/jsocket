/**
 * Javascript event's interface fail over HTTP
 */
var jsocketCoreHTTP = {
	api : null,
	initialized : false,
	connectedToServer : false,
	url : '',
	commands : [ ],

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
	* @parameters : {"cmd": "toto", "app": "tata", "channel": "titi", "uid": "*"}
	**/
	_post : function(parameters)
	{
		jsocketCoreHTTP.socket = false;
		//parameters = encodeURI('?json=' + parameters);
		parameters = encodeURI('?json={"test": "test"}');
		if (window.XMLHttpRequest) {
			jsocketCoreHTTP.socket = new XMLHttpRequest();
			if (jsocketCoreHTTP.socket.overrideMimeType) {
				jsocketCoreHTTP.socket.overrideMimeType('text/html');
			}
		}
		else if (window.ActiveXObject) {
			try {
				jsocketCoreHTTP.socket = new ActiveXObject("Msxml2.XMLHTTP");
			}
			catch (e) {
				try {
					jsocketCoreHTTP.socket = new ActiveXObject("Microsoft.XMLHTTP");
				}
				catch (e) { }
			}
		}
		if (!jsocketCoreHTTP.socket) {
			alert('Cannot create XMLHTTP instance');
			return (false);
		}
		jsocketCoreHTTP.socket.onreadystatechange = jsocketCoreHTTP.receive;
		jsocketCoreHTTP.socket.open('POST', 'http://' + jsocketCoreHTTP.api.host +
			':80/' + jsocketCoreHTTP.api.uid, true);
		jsocketCoreHTTP.socket.setRequestHeader("Content-type",
			"application/x-www-form-urlencoded");
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
		jsocketCoreHTTP.loaded();
		jsocketCoreHTTP.pool();
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
	* Pool le serveur HTTP en envoyant les requetes des n dernieres
	* secondes du client et pour obtenir les reponses des commandes
	* actuelles/precedentes
	* @void
	**/
	pool: function()
	{
		if (typeof jsocketCoreHTTP.api != 'object') {
			return (false);
		}
		jsocketCoreHTTP.write();
		//setTimeout("jsocketCoreHTTP.pool();", 2000);
	},

	/**
	* Envoie les commandes stockees prealablement au serveur.
	* @void
	**/
	write : function()
	{
		if (typeof jsocketCoreHTTP.api != 'object') {
			return (false);
		}
		msg = '';
		if (jsocketCoreHTTP.commands.length > 0) {
			msg = jsocketCoreHTTP.commands.join("\n")
			jsocketCoreHTTP.commands = [ ]
		}
		jsocketCoreHTTP._post(msg + "\n");
		return (true);
	},
 
	/**
	* Alias de write
	* @msg : String a envoye au serveur
	**/
	send : function(msg)
	{
		return (jsocketCoreHTTP.commands.push(msg));
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
	* Callback appele par socket lors de la reception d'un message
	* @void
	**/
	receive: function()
	{
		if (typeof jsocketCoreHTTP.api != 'object') {
			return (false);
		}
		if (jsocketCoreHTTP.socket.readyState == 4) {
			if (jsocketCoreHTTP.socket.status == 200) {
				msg = jsocketCoreHTTP.socket.responseText;
				if (jsocketCoreHTTP.connectedToServer == false) {
					jsocketCoreHTTP.connected();
				}
				if (msg != '') {
					res = msg.split("\n");
					for (var i = 0; res[i]; ++i) {
						jsocketCoreHTTP.api.onReceive(res[i]);
					}
				}
			} else {
				jsocketCoreHTTP.api.parser('{"from": "error", "value": "HTTP request error: ' +
					jsocketCoreHTTP.addslashes(jsocketCoreHTTP.socket.statusText) + '"}');
			}
		}
		return (true);
	}
};
