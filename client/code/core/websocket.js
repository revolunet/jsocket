/**
 * @class jsocket.core.websocket
 * Javascript event's interface for websocket HTML 5
 * @author Revolunet
 * @version 0.2.6
 * @singleton
 */
jsocket.core.websocket = {
	/**
	 * Pointeur vers l'API
	 * @private
	 * @type {@link jsocket.api}
	 */
	api: null,

	/**
	 * True si le core a ete initialize sinon False
	 * @private
	 * @type Boolean
	 */
	initialized: false,

	/**
	 * True si le core est connecte au server sinon False
	 * @private
	 * @type Boolean
	 */
	connectedToServer: false,

	/**
	 * True si ce core est utilise par l'API sinon False
	 * @private
	 * @type Boolean
	 */
	isWorking: false,

	/**
	 * Socket
	 * @private
	 * @type WebSocket
	 */
	socket: null,

	/**
	 * @event loaded
	 * Initialisation du code WebSocket
	 * @return {Boolean} True si l'application a ete chargee
	 */
	loaded: function() {
		if ('WebSocket' in window) {
			jsocket.core.websocket.initialized = true;
			jsocket.core.websocket.connectedToServer = false;
			return (true);
		}
		jsocket.core.websocket.initialized = false;
		jsocket.core.websocket.connectedToServer = false;
		return (false);
	},

	/**
	 * Initialise une connection via une socket sur le server:port
	 */
	connect: function() {
		if (jsocket.core.websocket.loaded() == false) {
			jsocket.core.websocket.api.parser('{"from": "WebSocketError", "value": "WebSocket not available"}');
			return (false);
		}
		if (jsocket.core.websocket.initialized == true && jsocket.core.websocket.connectedToServer == false) {
			jsocket.core.websocket.socket = new WebSocket('ws://' + jsocket.api.settings.websocket.host + ':' + jsocket.api.settings.websocket.port + '/jsocket');
			jsocket.core.websocket.socket.onmessage = jsocket.core.websocket.receive;
			jsocket.core.websocket.socket.onerror = jsocket.core.websocket.error;
			jsocket.core.websocket.socket.onopen = jsocket.core.websocket.connected;
			jsocket.core.websocket.socket.onclose = jsocket.core.websocket.disconnected;
		}
		else if (jsocket.core.websocket.connectedToServer == false) {
			jsocket.core.websocket.setTimeout("jsocket.core.websocket.connect();", 500);
		}
	},

	/**
	 * @event connected
	 * Callback appele par flash lorsque la socket est connectee au serveur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	connected: function() {
		if (typeof jsocket.core.websocket.api != 'object') {
			return (false);
		}
		jsocket.core.websocket.connectedToServer = true;
		jsocket.core.websocket.api.onReceive('{"from": "connect", "value": true}');
		jsocket.core.websocket.socket.send('{"cmd": "connected", "args": "null", "app": ""}');
		return (true);
	},

	/**
	 * @event disconnected
	 * Callback appele par flash lorsqu'une deconnection a ete effectuee
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	disconnected: function() {
		if (typeof jsocket.core.websocket.api != 'object') {
			return (false);
		}
		jsocket.core.websocket.api.uid = '';
		jsocket.core.websocket.api.parser('{"from": "disconnect", "value": true}');
		jsocket.core.websocket.connectedToServer = false;
		if (jsocket.core.websocket.manuallyDisconnected == true) {
			jsocket.core.websocket.manuallyDisconnected = false;
		} else {
			jsocket.core.websocket.connect();
		}
		return (true);
	},

	/**
	 * @event error
	 * Callback appele par WebSocket lorsqu'une erreur survient
	 * @param {String} msg Le message ainsi que le code d'erreur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	error: function(msg) {
		if (typeof jsocket.core.websocket.api != 'object') {
			return (false);
		}
		jsocket.core.websocket.api.parser('{"from": "WebSocketError", "value": "' + msg + '"}');
		return (true);
	},

	/**
	 * @event receive
	 * Callback appele par WebSocket lors de la reception d'un message
	 * @param {String} msg Le message envoye par le serveur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	receive: function(msg) {
		if (typeof jsocket.core.websocket.api != 'object') {
			return (false);
		}
		msg = msg.data;
		if (msg.data == '{"from": "connect", "value": "true"}') {
			jsocket.core.websocket.send('{"cmd": "connected", "args": "null", "app": ""}');
		}
		var tab = msg.split("\n");
		for (var i = 0; i < tab.length; ++i) {
			jsocket.core.websocket.api.onReceive(tab[i]);
		}
		return (true);
	},

	/**
	 * Lance un setTimeout sur cmd avec comme temps d'attente delay a
	 * condition que ce core est utilise par l'API
	 * @param {String} cmd La commande a lancer
	 * @param {Int} delay Le temps d'attente
	 */
	setTimeout: function(cmd, delay) {
		if (jsocket.core.websocket.isWorking == true) {
			setTimeout(cmd, delay);
		}
	},

	/**
	 * Addslashes les caracteres ' " \\ \0
	 * @param {String} str Le texte a addslasher
	 * @return {String} La chaine avec les caracteres echapes
	 */
	addslashes: function(str) {
		if (typeof(str) == 'string') {
			str = encodeURIComponent(str);
			str = str.replace(/\'/g, "%27");
		}
		else if (typeof(str) == 'object') {
			for (var i in str) {
				str[i] = jsocket.core.websocket.addslashes(str[i]);
			}
		}
		return (str);
	},

	/**
	 * Supprime tous les slashes des caracteres ' " \\ \0
	 * @param {String} str Le texte a stripslasher
	 * @return {String} La chaine avec les caracteres non echapes
	 */
	stripslashes: function (str) {
		if (typeof(str) == 'string') {
			str = str.replace(/\%27/g, "'");
			str = decodeURIComponent(str);
		}
		else if (typeof(str) == 'object') {
			for (var i in str) {
				str[i] = jsocket.core.websocket.stripslashes(str[i]);
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
	write: function(msg) {
		if (jsocket.core.websocket.connectedToServer == false) {
			jsocket.core.websocket.connect();
		}
		if (jsocket.core.websocket.connectedToServer) {
			jsocket.core.websocket.socket.send(msg + "\n");
		} else {
			if (typeof jsocket.core.websocket.api != 'object') {
				return (false);
			}
			jsocket.core.websocket.setTimeout("jsocket.core.websocket.send('" + msg + "');", 500);
			return (false);
		}
		return (true);
	},

	/**
	 * Alias de {@link #write write}
	 * @param {String} msg Le message a envoye au serveur
	 * @return {Boolean} True si le message a ete envoye sinon False
	 */
	send: function(msg) {
		return (jsocket.core.websocket.write(msg));
	},

	/**
	 * Ferme la connection au serveur
	 * @return {Boolean} True si la connection a ete fermee sinon False
	 */
	close: function() {
		jsocket.core.websocket.socket.close();
		return (true);
	}
};
