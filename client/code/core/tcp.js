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
     * True si le flash a appele le callback de load.
     * @private
     * @type Boolean
     */
    isLoaded: false,

    /**
     * Core name
     * @private
     * @type String
     */
    name: 'tcp',

    /**
     * Last try date time
     * @private
     * @type Integer
     */
    lastTry: false,

    /**
     * Flag lorsque la connection est ferme manuellement
     * @private
     * @type Boolean
     */
    manuallyDisconnected: false,

	/**
	 * @event loaded
	 * Callback appele par flash lorsque le swf est charge
	 * @return {Boolean} True si l'application a ete chargee
	 */
	loaded: function() {
        this.isLoaded = true;
		this.connectedToServer = false;
		this.socket = document.getElementById("socketBridge");
		this.output = document.getElementById("jsocketBridgeOutput");
		return (true);
	},

    /**
     * Retourne true si le core TCP est disponible, false sinon.
     * @return {Boolean} True si le core TCP est disponible, sinon false
     */
    isAvailable: function() {
        if (typeof navigator != 'undefined' &&
            typeof navigator.mimeTypes != 'undefined' &&
            typeof navigator.mimeTypes['application/x-shockwave-flash'] != 'undefined' &&
            navigator.mimeTypes["application/x-shockwave-flash"].enabledPlugin != null) {
            this.available = true;
        } else if (window.ActiveXObject) {
            try {
                var a = new ActiveXObject("ShockwaveFlash.ShockwaveFlash");
                this.available = true;
            } catch (oError) {
                this.available = false;
            }
        } else {
            this.available = false;
        }
        return (this.available);
    },

	/**
	 * Initialise une connection via une socket sur le server:port
	 */
	connect: function() {
        if (this.lastTry == false) {
            this.lastTry = new Date().getTime();
        }
        if (this.available == false) {
            this.api.parser(jsocket.utils.forge({from: 'TCPError',
                                                 value: 'TCP is not available'}));
            return (false);
        }
        if (new Date().getTime() - this.lastTry > 2000) {
            this.api.parser(jsocket.utils.forge({from: 'TCPError',
                                                 value: 'TCP is not available'}));
            return (false);
        }
		if (this.isLoaded == true &&
            this.connectedToServer == false) {
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
        this.lastTry = false;
		this.connectedToServer = true;
        this.keepAlive();
		this.send(jsocket.utils.forge({
                    cmd: 'connected',
                    args: {vhost: this.api.settings.vhost}}));
		return (true);
	},

    /**
     * Send keep alive request to server to prevent watchdog to delete client.
     */
    keepAlive: function() {
        if (this.connectedToServer && this.isWorking) {
            this.api.send(jsocket.utils.forge({cmd: 'keepalive',
                                               uid: '.uid.'}));
        }
        if (this.isWorking) {
            this.setTimeout(this.keepAlive, this.api.settings.keepAliveTimer);
        }
    },

	/**
	 * Ferme la connection au serveur
	 * @return {Boolean} True si la connection a ete fermee sinon False
	 */
	close: function() {
        if (this.socket) {
            this.manuallyDisconnected = true;
            this.socket.close();
            this.disconnected();
        }
		return (true);
	},

	/**
	 * @event disconnected
	 * Callback appele par flash lorsqu'une deconnection a ete effectuee
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	disconnected: function() {
		this.api.uid = '';
		this.api.parser(jsocket.utils.forge({from: 'disconnect', value: true}));
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
	 * @event ioError
	 * Callback appele par flash lorsqu'une Input/Output erreur survient
	 * @param {String} msg Le message ainsi que le code d'erreur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	ioError: function(msg) {
		this.api.parser(jsocket.utils.forge({from: 'error', value: msg}));
		if (this.connectedToServer == false) {
			this.api.parser(jsocket.utils.forge({from: 'TCPError', value: 'Input/Output error'}));
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
		this.api.parser(jsocket.utils.forge({from: 'error', value: msg}));
		if (this.connectedToServer == false) {
			this.api.parser(jsocket.utils.forge({from: 'TCPError', value: 'Security error'}));
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
		var tab = decodeURIComponent(msg).split("\n");
		for (var i = 0; i < tab.length; ++i) {
			this.api.onReceive(tab[i]);
		}
		return (true);
	}
};
