/**
 * Javascript event's interface for flash swf socket bridge
 */
var jsocketCore = {
	api : null,
	initialized : false,
	connectedToServer : false,

	/**
	* Callback appele par flash lorsque le swf est charge
	* @void
	**/
	loaded : function()
	{
		jsocketCore.initialized = true;
		jsocketCore.connectedToServer = false;
		jsocketCore.socket = document.getElementById("socketBridge");
		jsocketCore.output = document.getElementById("jsocketBridgeOutput");
		return (true);
	},
 
	/**
	* Initialise une connection via une socket sur le server:port
	* @server : Hostname ou adresse IP du serveur
	* @port : Numero du port du serveur
	**/
	connect : function(server, port)
	{
		if (jsocketCore.initialized == true && jsocketCore.connectedToServer == false) {
			jsocketCore.socket.connect(server, port);
		}
		else if (jsocketCore.connectedToServer == false) {
			setTimeout("jsocketCore.reconnect();", 500);
		}
	},
 
	/**
	* Alias de connect sans avoir a repreciser les parametres de connection
	* @void
	**/
	reconnect : function()
	{
		jsocketCore.connect(jsocketCore.api.host, jsocketCore.api.port);
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
				str[i] = jsocketCore.addslashes(str[i]);
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
				str[i] = jsocketCore.stripslashes(str[i]);
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
		if (jsocketCore.connectedToServer == false) {
			jsocketCore.reconnect();
		}
		if (jsocketCore.connectedToServer) {
			jsocketCore.socket.write(msg + "\n");
		}
		else {
			if (typeof jsocketCore.api != 'object') {
				return (false);
			}
			setTimeout("jsocketCore.send('" + msg + "');", 500);
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
		return (jsocketCore.write(msg));
	},
 
	/**
	* Callback appele par flash lorsque la socket est connectee au serveur
	* @void
	**/
	connected : function()
	{
		if (typeof jsocketCore.api != 'object') {
			return (false);
		}
		jsocketCore.connectedToServer = true;
		jsocketCore.api.onReceive('{"from": "connect", "value": true}');
		return (true);
	},
 
	/**
	* Ferme la connection au serveur
	* @void
	**/
	close : function()
	{
		jsocketCore.socket.close();
		return (true);
	},
 
	/**
	* Callback appele par flash lorsqu'une deconnection a ete effectuee
	* @void
	**/
	disconnected : function()
	{
		if (typeof jsocketCore.api != 'object') {
			return (false);
		}
		jsocketCore.api.parser('{"from": "disconnect", "value": true}');
		jsocketCore.connectedToServer = false;
		jsocketCore.reconnect();
		return (true);
	},
 
	/**
	* Callback appele par flash lorsqu'une Input/Output erreur survient
	* @msg : Message + Code d'erreur
	**/
	ioError: function(msg)
	{
		if (typeof jsocketCore.api != 'object') {
			return (false);
		}
		jsocketCore.api.parser('{"from": "error", "value": "' + msg + '"}');
		if (jsocketCore.connectedToServer == false) {
			jsocketCore.reconnect();
		}
		return (true);
	},
 
	/**
	* Callback appele par flash lorsqu'une erreur de securite survient
	* @msg : Message + Code d'erreur
	**/
	securityError: function(msg)
	{
		if (typeof jsocketCore.api != 'object') {
			return (false);
		}
		jsocketCore.api.parser('{"from": "error", "value": "' + msg + '"}');
		if (jsocketCore.connectedToServer == false) {
			jsocketCore.reconnect();
		}
		return (true);
	},
 
	/**
	* Callback appele par flash lors de la reception d'un message via la socket
	* @msg : Texte envoye par le serveur
	**/
	receive: function(msg)
	{
		if (typeof jsocketCore.api != 'object') {
			return (false);
		}
		jsocketCore.api.onReceive(msg);
		return (true);
	}
};
