/**
 * @class jsocket.core.tcp
 * Javascript event's interface for flash swf socket bridge
 * @author Revolunet
 * @version 0.3.0
 * @singleton
 */
jsocket.core.tcp = {
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
	available: false,

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
	 * @event loaded
	 * Callback appele par flash lorsque le swf est charge
	 * @return {Boolean} True si l'application a ete chargee
	 */
	loaded: function() {
		this.available = true;
		this.connectedToServer = false;
		this.socket = document.getElementById("socketBridge");
		this.output = document.getElementById("jsocketBridgeOutput");
		return (true);
	},

	/**
	 * Initialise une connection via une socket sur le server:port
	 */
	connect: function() {
        if (this.available == false) {
            this.api.parser('{"from": "TCPError", "value": "TCP is not available"}');
            return (false);
        }
		if (this.connectedToServer == false) {
			this.socket.connect(this.api.settings.tcp.host, this.api.settings.tcp.port);
		} else if (this.connectedToServer == false) {
			this.setTimeout(this.connect, 500);
		}
        return (true);
	},

	/**
	 * Lance un setTimeout sur cmd avec comme temps d'attente delay a
	 * condition que ce core est utilise par l'API
	 * @param {String} cmd La commande a lancer
	 * @param {Int} delay Le temps d'attente
	 */
	setTimeout: function(method, delay, args) {
		if (this.isWorking == true) {
            if (args) {
                jsocket.utils.defer(method, delay, this, args);
            } else {
                jsocket.utils.defer(method, delay, this);
            }
		}
	},

	/**
	 * Envoie le message au serveur.
	 * Tentative de reconnection a ce dernier le cas echeant.
	 * @param {String} msg Le texte a envoyer au serveur
	 * @return {Boolean} True si le message a ete envoye sinon False
	 */
	write: function(msg) {
		if (this.connectedToServer == false) {
			this.connect();
		}
		if (this.connectedToServer) {
			this.socket.write(msg + "\n");
		} else {
			if (typeof this.api != 'object') {
				return (false);
			}
			this.setTimeout(this.send, 500, msg);
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
		return (this.write(msg));
	},

	/**
	 * @event connected
	 * Callback appele par flash lorsque la socket est connectee au serveur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	connected: function() {
		if (typeof this.api != 'object') {
			return (false);
		}
		this.connectedToServer = true;
		this.send('{"cmd": "connected", "args": { "vhost":"' + this.api.settings.vhost + '" }, "app": ""}');
		this.api.onReceive('{"from": "connect", "value": true}');
		return (true);
	},

	/**
	 * Ferme la connection au serveur
	 * @return {Boolean} True si la connection a ete fermee sinon False
	 */
	close: function() {
		this.socket.close();
		this.connectedToServer = false;
		return (true);
	},

	/**
	 * @event disconnected
	 * Callback appele par flash lorsqu'une deconnection a ete effectuee
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	disconnected: function() {
		if (typeof this.api != 'object') {
			return (false);
		}
		this.api.uid = '';
		this.api.parser('{"from": "disconnect", "value": true}');
		this.connectedToServer = false;
		this.connect();
		return (true);
	},

	/**
	 * @event ioError
	 * Callback appele par flash lorsqu'une Input/Output erreur survient
	 * @param {String} msg Le message ainsi que le code d'erreur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	ioError: function(msg) {
		if (typeof this.api != 'object') {
			return (false);
		}
		this.api.parser('{"from": "error", "value": "' + msg + '"}');
		if (this.connectedToServer == false) {
			this.api.parser('{"from": "TCPError", "value": "Input/Output error"}');
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
		if (typeof this.api != 'object') {
			return (false);
		}
		this.api.parser('{"from": "error", "value": "' + msg + '"}');
		if (this.connectedToServer == false) {
			this.api.parser('{"from": "TCPError", "value": "Security error"}');
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
		if (typeof this.api != 'object') {
			return (false);
		}
		var tab = decodeURIComponent(msg).split("\n");
		for (var i = 0; i < tab.length; ++i) {
			this.api.onReceive(tab[i]);
		}
		return (true);
	}
};
