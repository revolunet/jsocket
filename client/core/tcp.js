/**
 * @class jsocket.core.tcp
 * Javascript event's interface for flash swf socket bridge
 * @author Revolunet
 * @version 0.2.5
 * @singleton
 */
jsocket.core.tcp = {
	/**
	 * Pointeur vers l'API
	 * @private
	 * @type {@link jsocket.api}
	 */
	api : null,

	/**
	 * True si le core a ete initialize sinon False
	 * @private
	 * @type Boolean
	 */
	initialized : false,

	/**
	 * True si le core est connecte au server sinon False
	 * @private
	 * @type Boolean
	 */
	connectedToServer : false,

	/**
	 * True si ce core est utilise par l'API sinon False
	 * @private
	 * @type Boolean
	 */
	isWorking : false,

	/**
	 * @event loaded
	 * Callback appele par flash lorsque le swf est charge
	 * @return {Boolean} True si l'application a ete chargee
	 */
	loaded : function() {
		jsocket.core.tcp.initialized = true;
		jsocket.core.tcp.connectedToServer = false;
		jsocket.core.tcp.socket = document.getElementById("socketBridge");
		jsocket.core.tcp.output = document.getElementById("jsocketBridgeOutput");
		return (true);
	},

	/**
	 * Initialise une connection via une socket sur le server:port
	 * @param {String} server Le nom de domaine ou adresse IP du serveur
	 * @param {Int} port Le numero du port du serveur
	 */
	connect : function(server, port) {
		if (jsocket.core.tcp.initialized == true && jsocket.core.tcp.connectedToServer == false) {
			jsocket.core.tcp.socket.connect(server, port);
		}
		else if (jsocket.core.tcp.connectedToServer == false) {
			jsocket.core.tcp.setTimeout("jsocket.core.tcp.reconnect();", 500);
		}
	},

	/**
	 * Alias de {@link #connect connect} sans avoir a repreciser les parametres de connection
	 */
	reconnect : function() {
		jsocket.core.tcp.connect(jsocket.core.tcp.api.host, jsocket.core.tcp.api.port);
	},

	/**
	 * Lance un setTimeout sur cmd avec comme temps d'attente delay a
	 * condition que ce core est utilise par l'API
	 * @param {String} cmd La commande a lancer
	 * @param {Int} delay Le temps d'attente
	 */
	setTimeout : function(cmd, delay) {
		if (jsocket.core.tcp.isWorking == true) {
			setTimeout(cmd, delay);
		}
	},

	/**
	 * Addslashes les caracteres ' " \\ \0
	 * @param {String} str Le texte a addslasher
	 * @return {String} La chaine avec les caracteres echapes
	 */
	addslashes : function(str) {
		if (typeof(str) == 'string') {
			str = encodeURIComponent(str);
			str = str.replace(/\'/g, "%27");
		}
		else if (typeof(str) == 'object') {
			for (var i in str) {
				str[i] = jsocket.core.tcp.addslashes(str[i]);
			}
		}
		return (str);
	},

	/**
	 * Supprime tous les slashes des caracteres ' " \\ \0
	 * @param {String} str Le texte a stripslasher
	 * @return {String} La chaine avec les caracteres non echapes
	 */
	stripslashes : function (str) {
		if (typeof(str) == 'string') {
			str = str.replace(/\%27/g, "'");
			str = decodeURIComponent(str);
		}
		else if (typeof(str) == 'object') {
			for (var i in str) {
				str[i] = jsocket.core.tcp.stripslashes(str[i]);
			}
		}
		return (str);
	},

	/**
	 * Envoie le message au serveur.
	 * Tentative de reconnection a ce dernier le cas echeant.
	 * @param {String} msg Le texte a envoyer au serveur
	 * @return {Boolean} True si le message a ete envoye sinon False
	 */
	write : function(msg) {
		if (jsocket.core.tcp.connectedToServer == false) {
			jsocket.core.tcp.reconnect();
		}
		if (jsocket.core.tcp.connectedToServer) {
			jsocket.core.tcp.socket.write(msg + "\n");
		} else {
			if (typeof jsocket.core.tcp.api != 'object') {
				return (false);
			}
			jsocket.core.tcp.setTimeout("jsocket.core.tcp.send('" + msg + "');", 500);
			return (false);
		}
		return (true);
	},

	/**
	 * Alias de {@link #write write}
	 * @param {String} msg Le message a envoye au serveur
	 * @return {Boolean} True si le message a ete envoye sinon False
	 */
	send : function(msg) {
		return (jsocket.core.tcp.write(msg));
	},

	/**
	 * @event connected
	 * Callback appele par flash lorsque la socket est connectee au serveur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	connected : function() {
		if (typeof jsocket.core.tcp.api != 'object') {
			return (false);
		}
		jsocket.core.tcp.connectedToServer = true;
		jsocket.core.tcp.send('{"cmd": "connected", "args": "null", "app": ""}');
		jsocket.core.tcp.api.onReceive('{"from": "connect", "value": true}');
		return (true);
	},

	/**
	 * Ferme la connection au serveur
	 * @return {Boolean} True si la connection a ete fermee sinon False
	 */
	close : function() {
		jsocket.core.tcp.socket.close();
		return (true);
	},

	/**
	 * @event disconnected
	 * Callback appele par flash lorsqu'une deconnection a ete effectuee
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	disconnected : function() {
		if (typeof jsocket.core.tcp.api != 'object') {
			return (false);
		}
		jsocket.core.tcp.api.uid = '';
		jsocket.core.tcp.api.parser('{"from": "disconnect", "value": true}');
		jsocket.core.tcp.connectedToServer = false;
		jsocket.core.tcp.reconnect();
		return (true);
	},

	/**
	 * @event ioError
	 * Callback appele par flash lorsqu'une Input/Output erreur survient
	 * @param {String} msg Le message ainsi que le code d'erreur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	ioError: function(msg) {
		if (typeof jsocket.core.tcp.api != 'object') {
			return (false);
		}
		jsocket.core.tcp.api.parser('{"from": "error", "value": "' + msg + '"}');
		if (jsocket.core.tcp.connectedToServer == false) {
			jsocket.core.tcp.api.parser('{"from": "TCPError", "value": "Input/Output error"}');
		}
		return (true);
	},

	/**
	 * @event securityError
	 * Callback appele par flash lorsqu'une erreur de securite survient
	 * @param {String} msg Le message ainsi que le code d'erreur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	securityError: function(msg) {
		if (typeof jsocket.core.tcp.api != 'object') {
			return (false);
		}
		jsocket.core.tcp.api.parser('{"from": "error", "value": "' + msg + '"}');
		if (jsocket.core.tcp.connectedToServer == false) {
			jsocket.core.tcp.api.parser('{"from": "TCPError", "value": "Security error"}');
		}
		return (true);
	},

	/**
	 * @event receive
	 * Callback appele par flash lors de la reception d'un message via la socket
	 * @param {String} msg Le message envoye par le serveur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	receive: function(msg) {
		if (typeof jsocket.core.tcp.api != 'object') {
			return (false);
		}
		var tab = msg.split("\n");
		for (var i = 0; i < tab.length; ++i) {
			jsocket.core.tcp.api.onReceive(tab[i]);
		}
		return (true);
	}
};