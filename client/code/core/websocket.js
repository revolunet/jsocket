/**
 * @class jsocket.core.websocket
 * Javascript event's interface for websocket HTML 5
 * @author Revolunet
 * @version 0.3.0
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
        this.connectedToServer = false;
		if ('WebSocket' in window) {
			this.available = true;
		} else {
            this.available = false;
        }
		return (this.available);
	},

	/**
	 * Initialise une connection via une socket sur le server:port
	 */
	connect: function() {
		if (this.available == false) {
			this.api.parser('{"from": "WebSocketError", "value": "WebSocket not available"}');
			return (false);
		}
		if (!this.socket) {
			this.socket = new WebSocket('ws://' + this.api.settings.websocket.host +
                                        ':' + this.api.settings.websocket.port + '/jsocket');
			this.socket.onmessage = jsocket.utils.createDelegate(this.receive, this);
			this.socket.onerror = jsocket.utils.createDelegate(this.error, this);
			this.socket.onopen = jsocket.utils.createDelegate(this.connected, this);
			this.socket.onclose = jsocket.utils.createDelegate(this.disconnected, this);
		}
		else if (this.connectedToServer == false) {
			this.setTimeout(this.connect, 500);
		}
        return (true);
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
        this.keepAlive();
		this.socket.send('{"cmd": "connected", "args": { "vhost":"' + this.api.settings.vhost + '" }, "app": "" }');
		return (true);
	},

    /**
     * Send keep alive request to server to prevent watchdog to delete client.
     */
    keepAlive: function() {
        if (this.connectedToServer && this.isWorking) {
            this.api.send(jsocket.utils.forge({
                        cmd: 'keepalive',
                        uid: '.uid.'}));
        }
        if (this.isWorking) {
            this.setTimeout(this.keepAlive, this.api.settings.keepAliveTimer);
        }
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
		if (this.connectedToServer == false) {
			return (false);
		}
		this.connectedToServer = false;
		if (this.manuallyDisconnected == true) {
			this.manuallyDisconnected = false;
		} else {
			this.connect();
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
		if (typeof this.api != 'object') {
			return (false);
		}
		this.api.parser('{"from": "WebSocketError", "value": "' + msg + '"}');
		return (true);
	},

	/**
	 * @event receive
	 * Callback appele par WebSocket lors de la reception d'un message
	 * @param {String} msg Le message envoye par le serveur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	receive: function(msg) {
		if (typeof this.api != 'object') {
			return (false);
		}
		msg = msg.data;
		var tab = msg.split("\n");
		for (var i = 0; i < tab.length; ++i) {
			this.api.onReceive(tab[i]);
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
			this.socket.send(msg + "\n");
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
	 * Ferme la connection au serveur
	 * @return {Boolean} True si la connection a ete fermee sinon False
	 */
	close: function() {
		if (this.socket != null) {
			this.manuallyDisconnected = true;
            this.socket.close();
        }
		return (true);
	}
};
