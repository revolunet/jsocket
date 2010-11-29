/**
 * @class jsocket.core.http
 * Javascript event's interface fail over HTTP
 * @author Revolunet
 * @version 0.3.0
 * @singleton
 */
jsocket.core.http = {
	/**
	 * <p><b><u>Response:</u></b></p>
	 * <div class="mdetail-params"><ul>
	 * <li><b><tt>waiting: true si une requete est en attente de reponse sinon false</tt></b></li>
	 * <li><b><tt>lastTime: timestamp de la derniere reponse obtenue</tt></b></li>
	 * <li><b><tt>timeout: temps en seconde avant de relancer une requete si il n'y a pas
	 * eu de reponse positive entre temps</tt></b></li>
	 * </ul></div></p>
	 * @public
	 * @type Object
	 */
	response: {
		waiting: false,
		lastTime: 0,
		timeout: 5
	},

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
	 * Liste des commandes en attente
	 * @private
	 * @type Array
	 */
	commands: [],

	/**
	 * True si ce core est utilise par l'API sinon False
	 * @private
	 * @type Boolean
	 */
	isWorking: false,

    /**
     * Core name
     * @private
     * @type String
     */
    name: 'http',

	/**
	 * Return true si le core HTTP est disponible, sinon false.
	 * @return {Boolean} True si le code HTTP est disponible, sinon false
	 */
	isAvailable: function()	{
		this.available = true;
		return (this.available);
	},

    /**
     * Permet d'effectuer une request HTTP GET sur le server (host, port)
     * @param {String} parameters La commande JSON a envoyee
     * @return {Boolean} True si la commande a ete envoyee sinon False
     */
    _get: function(parameters) {
        parameters = encodeURI('json=' + parameters);
        var el = document.createElement('script');
        el.type = 'text/javascript';
        el.onload = this.receive;
        el.onreadystatechange = this.receive;
        el.src = this.api.settings.http.url + '?' + parameters + '&ts=' + new Date().getTime();
        document.body.appendChild(el);
		this.response.waiting = true;
        return (true);
    },

	/**
	 * Initialise une connection via une socket sur le server:port
	 */
	connect: function() {
        if (this.connectedToServer == true) {
            return (false);
        }
        
        this._get('{ "cmd": "connected", "args": { "vhost": "' + this.api.settings.vhost + '" }}');
      
		this.pool();
        this.response.waiting = false;
        return (true);
	},

	/**
	 * Pool le serveur HTTP en envoyant les requetes des n dernieres
	 * secondes du client et pour obtenir les reponses des commandes
	 * actuelles/precedentes
	 * @return {Boolean} False si l'API n'est pas definie
	 */
	pool: function() {
		if (this.isWorking == false) {
			return (false);
		}
        if (this.connectedToServer == true) {
            this.write();
        }
		jsocket.utils.defer(this.pool, this.api.settings.http.refreshTimer, this);
	},

	/**
	 * Ferme la connection au serveur
	 * @return {Boolean} True si la connection a ete fermee sinon False
	 */
	close: function() {
		this.connectedToServer = false;
        this._get(jsocket.utils.forge({
                    cmd: 'disconnected',
                    uid: this.api.uid}));
		return (true);
	},

	/**
	 * Verifie si une commande peut etre envoye au serveur
	 * @return {Boolean} True si la commande peut etre envoyee sinon False
	 */
	checkResponse: function() {
		var now = Math.floor(new Date().getTime() / 1000);
		if (this.response.waiting == false) {
			return (true);
		} else if ((now - this.response.lastTime) > this.response.timeout) {
			this.response.lastTime = now;
			return (true);
		}
		return (false);
	},

	/**
	 * Envoie les commandes stockees prealablement au serveur.
	 * @return {Boolean} True si les commandes ont ete envoyees sinon False
	 */
	write: function() {
		if (this.checkResponse() == false) {
			return (false);
		}
		msg = '';
		if (this.commands.length > 0) {
			msg = this.commands.join("\n");
			this.commands = [];
            this._get(msg + "\n");
		} else {
            this._get(jsocket.utils.forge({
                        cmd: 'refresh',
                        uid: this.api.uid}));
		}
		return (true);
	},

	/**
	 * Alias de {@link #write write}
	 * @param {String} msg Le message a envoye au serveur
	 * @return {Boolean} True si le message a ete envoye sinon False
	 */
	send: function(msg) {
		if (msg.length > 0) {
			return (this.commands.push(msg));
		}
		return (false);
	},

	/**
	 * @event connected
	 * Callback appele par flash lorsque la socket est connectee au serveur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	connected: function() {
		this.connectedToServer = true;
		return (true);
	},

	/**
	 * @event disconnected
	 * Callback appele par flash lorsqu'une deconnection a ete effectuee
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	disconnected: function() {
		this.api.parser(jsocket.utils.forge({from: 'disconnect', value: true}));
		this.connectedToServer = false;
		this.connect();
		return (true);
	},

	/**
	 * @event receive
	 * Callback appele par socket lors de la reception d'un message
	 * @return {Boolean} True si la commande a ete envoyee a l'API sinon False
	 */
    receive: function() {
        if (this.readyState &&
            (this.readyState == "loaded" ||
             this.readyState == "complete") &&
            this.parentNode) {
            this.parentNode.removeChild(this);
        } else if (this.readyState != "loading" && this.parentNode) {
            this.parentNode.removeChild(this);
        }
		if (typeof jsocket.core.http.api != 'object') {
			return (false);
		}
        if (jsocket.core.http.connectedToServer == false) {
            jsocket.core.http.connected();
        }
        jsocket.core.http.response.waiting = false;
        jsocket.core.http.response.lastTime = Math.floor(new Date().getTime() / 1000);
		return (true);
    }
};
