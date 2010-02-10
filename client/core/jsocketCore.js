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
		this.initialized = true;
		this.connectedToServer = false;
		this.socket = document.getElementById("socketBridge");
		this.output = document.getElementById("jsocketBridgeOutput");
		return (true);
	},
 
	/**
	* Initialise une connection via une socket sur le server:port
	* @server : Hostname ou adresse IP du serveur
	* @port : Numero du port du serveur
	**/
	connect : function(server, port)
	{
		if (this.initialized == true && this.connectedToServer == false) {
			this.socket.connect(server, port);
		}
		else {
			setTimeout("jsocketCore.reconnect();", 500);
		}
	},
 
	/**
	* Alias de connect sans avoir a repreciser les parametres de connection
	* @void
	**/
	reconnect : function()
	{
		this.connect(this.api.host, this.api.port);
	},

	/**
	* Addslashes les caracteres ' " \\ \0
	* @str : Texte a addslasher
	**/
	addslashes : function(str)
	{
		str = str.replace(/\\/g, '\\\\');
		str = str.replace(/\'/g, '\\\'');
		str = str.replace(/\"/g, '\\"');
		str = str.replace(/\0/g, '\\0');
		return (str);
	},
 
	/**
	* Supprime tous les slashes des caracteres \' \" \\0 \\\\
	* @str : Texte a stripslasher
	**/
	stripslashes : function (str)
	{
		str = str.replace(/\\'/g, '\'');
		str = str.replace(/\\"/g, '"');
		str = str.replace(/\\0/g, '\0');
		str = str.replace(/\\\\/g, '\\');
		return (str);
	},

	/**
	* Envoie le message au serveur.
	* Tentative de reconnection a ce dernier le cas echeant.
	* @msg : Texte a envoyer au serveur
	**/
	write : function(msg)
	{
		if (this.connectedToServer == false) {
			this.reconnect();
		}
		if (this.connectedToServer) {
			this.socket.write(msg);
		}
		else {
			if (typeof this.api != 'object') {
				return (false);
			}
			setTimeout("jsocketCore.send('" + msg + "');", 500);
			//this.api.onDisconnect('{"from": "disconnect", "value": "True"}');
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
		return (this.write(msg));
	},
 
	/**
	* Callback appele par flash lorsque la socket est connectee au serveur
	* @void
	**/
	connected : function()
	{
		if (typeof this.api != 'object') {
			return (false);
		}
		this.connectedToServer = true;
		this.api.onConnect('{"from": "connect", "value": true}');
		return (true);
	},
 
	/**
	* Ferme la connection au serveur
	* @void
	**/
	close : function()
	{
		this.socket.close();
		return (true);
	},
 
	/**
	* Callback appele par flash lorsqu'une deconnection a ete effectuee
	* @void
	**/
	disconnected : function()
	{
		if (typeof this.api != 'object') {
			return (false);
		}
		//this.api.onDisconnect('{"from": "disconnect", "value": "true"}');
		this.connectedToServer = false;
		this.reconnect();
		return (true);
	},
 
	/**
	* Callback appele par flash lorsqu'une Input/Output erreur survient
	* @msg : Message + Code d'erreur
	**/
	ioError: function(msg)
	{
		if (typeof this.api != 'object') {
			return (false);
		}
		this.api.onError('{"from": "ioError", "value": "' + msg + '"}');
		if (this.connectedToServer == false) {
			this.reconnect();
		}
		return (true);
	},
 
	/**
	* Callback appele par flash lorsqu'une erreur de securite survient
	* @msg : Message + Code d'erreur
	**/
	securityError: function(msg)
	{
		if (typeof this.api != 'object') {
			return (false);
		}
		this.api.onError('{"from": "securityError", "value": "' + msg + '"}');
		if (this.connectedToServer == false) {
			this.reconnect();
		}
		return (true);
	},
 
	/**
	* Callback appele par flash lors de la reception d'un message via la socket
	* @msg : Texte envoye par le serveur
	**/
	receive: function(msg)
	{
		if (typeof this.api != 'object') {
			return (false);
		}
		this.api.onReceive(msg);
		return (true);
	},
};