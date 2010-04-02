/**
 * Javascript event's interface for flash swf socket bridge
 */
var jsocketCoreTCP = {
	api : null,
	initialized : false,
	connectedToServer : false,
	isWorking : false,

	/**
	* Callback appele par flash lorsque le swf est charge
	* @void
	**/
	loaded : function()
	{
		jsocketCoreTCP.initialized = true;
		jsocketCoreTCP.connectedToServer = false;
		jsocketCoreTCP.socket = document.getElementById("socketBridge");
		jsocketCoreTCP.output = document.getElementById("jsocketBridgeOutput");
		return (true);
	},
 
	/**
	* Initialise une connection via une socket sur le server:port
	* @server : Hostname ou adresse IP du serveur
	* @port : Numero du port du serveur
	**/
	connect : function(server, port)
	{
		if (jsocketCoreTCP.initialized == true && jsocketCoreTCP.connectedToServer == false) {
			jsocketCoreTCP.socket.connect(server, port);
		}
		else if (jsocketCoreTCP.connectedToServer == false) {
			jsocketCoreTCP.setTimeout("jsocketCoreTCP.reconnect();", 500);
		}
	},
 
	/**
	* Alias de connect sans avoir a repreciser les parametres de connection
	* @void
	**/
	reconnect : function()
	{
		jsocketCoreTCP.connect(jsocketCoreTCP.api.host, jsocketCoreTCP.api.port);
	},

	/**
	* Lance un setTimeout sur cmd avec comme temps d'attente delay a
	* condition que ce core est utilise par l'API
	* @cmd : La commande a lancer
	* @delay : Le temps d'attente
	**/
	setTimeout : function(cmd, delay) {
		if (jsocketCoreTCP.isWorking == true) {
			setTimeout(cmd, delay);
		}
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
				str[i] = jsocketCoreTCP.addslashes(str[i]);
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
				str[i] = jsocketCoreTCP.stripslashes(str[i]);
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
		if (jsocketCoreTCP.connectedToServer == false) {
			jsocketCoreTCP.reconnect();
		}
		if (jsocketCoreTCP.connectedToServer) {
			jsocketCoreTCP.socket.write(msg + "\n");
		}
		else {
			if (typeof jsocketCoreTCP.api != 'object') {
				return (false);
			}
			jsocketCoreTCP.setTimeout("jsocketCoreTCP.send('" + msg + "');", 500);
			return (false);
		}
		return (true);
	},
 
	/**
	* Alias de write
	* @msg : String a envoye au serveur
	**/
	send : function(msg)
	{
		return (jsocketCoreTCP.write(msg));
	},
 
	/**
	* Callback appele par flash lorsque la socket est connectee au serveur
	* @void
	**/
	connected : function()
	{
		if (typeof jsocketCoreTCP.api != 'object') {
			return (false);
		}
		jsocketCoreTCP.connectedToServer = true;
		jsocketCoreTCP.send('{"cmd": "connected", "args": "null", "app": ""}');
		jsocketCoreTCP.api.onReceive('{"from": "connect", "value": true}');
		return (true);
	},
 
	/**
	* Ferme la connection au serveur
	* @void
	**/
	close : function()
	{
		jsocketCoreTCP.socket.close();
		return (true);
	},
 
	/**
	* Callback appele par flash lorsqu'une deconnection a ete effectuee
	* @void
	**/
	disconnected : function()
	{
		if (typeof jsocketCoreTCP.api != 'object') {
			return (false);
		}
		jsocketCoreTCP.api.uid = '';
		jsocketCoreTCP.api.parser('{"from": "disconnect", "value": true}');
		jsocketCoreTCP.connectedToServer = false;
		jsocketCoreTCP.reconnect();
		return (true);
	},
 
	/**
	* Callback appele par flash lorsqu'une Input/Output erreur survient
	* @msg : Message + Code d'erreur
	**/
	ioError: function(msg)
	{
		if (typeof jsocketCoreTCP.api != 'object') {
			return (false);
		}
		jsocketCoreTCP.api.parser('{"from": "error", "value": "' + msg + '"}');
		if (jsocketCoreTCP.connectedToServer == false) {
			//jsocketCoreTCP.reconnect();
			jsocketCoreTCP.api.parser('{"from": "TCPError", "value": "Input/Output error"}');
		}
		return (true);
	},
 
	/**
	* Callback appele par flash lorsqu'une erreur de securite survient
	* @msg : Message + Code d'erreur
	**/
	securityError: function(msg)
	{
		if (typeof jsocketCoreTCP.api != 'object') {
			return (false);
		}
		jsocketCoreTCP.api.parser('{"from": "error", "value": "' + msg + '"}');
		if (jsocketCoreTCP.connectedToServer == false) {
			//jsocketCoreTCP.reconnect();
			jsocketCoreTCP.api.parser('{"from": "TCPError", "value": "Security error"}');
		}
		return (true);
	},
 
	/**
	* Callback appele par flash lors de la reception d'un message via la socket
	* @msg : Texte envoye par le serveur
	**/
	receive: function(msg)
	{
		if (typeof jsocketCoreTCP.api != 'object') {
			return (false);
		}
		var tab = msg.split("\n");
		for (var i = 0; i < tab.length; ++i) {
			jsocketCoreTCP.api.onReceive(tab[i]);
		}
		return (true);
	}
};
