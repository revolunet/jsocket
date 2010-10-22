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
	initialized: false,

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
	commands: [ ],

	/**
	 * True si ce core est utilise par l'API sinon False
	 * @private
	 * @type Boolean
	 */
	isWorking: false,

	/**
	 * Initialisation du core HTTP
	 * @return {Boolean} True si l'application a ete chargee
	 */
	loaded: function()	{
		jsocket.core.http.initialized = true;
		return (true);
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
        el.onload = jsocket.core.http.receive;
        el.onreadystatechange = jsocket.core.http.receive;
        el.src = jsocket.api.settings.http.url + '?' + parameters + '&ts=' + new Date().getTime();
        document.body.appendChild(el);
		jsocket.core.http.response.waiting = true;
        return (true);
    },

	/**
	 * Initialise une connection via une socket sur le server:port
	 */
	connect: function() {
		jsocket.core.http.loaded();
		jsocket.core.http.send('{"cmd": "connected", "args": { "vhost":"' + jsocket.api.settings.vhost + '" }, "app": ""}');
		jsocket.core.http.pool();
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
				str[i] = jsocket.core.http.addslashes(str[i]);
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
				str[i] = jsocket.core.http.stripslashes(str[i]);
			}
		}
		return (str);
	},

	/**
	 * Pool le serveur HTTP en envoyant les requetes des n dernieres
	 * secondes du client et pour obtenir les reponses des commandes
	 * actuelles/precedentes
	 * @return {Boolean} False si l'API n'est pas definie
	 */
	pool: function() {
		if (typeof jsocket.core.http.api != 'object' || jsocket.core.http.isWorking == false) {
			return (false);
		}
		jsocket.core.http.write();
		setTimeout("jsocket.core.http.pool();", jsocket.api.settings.http.refreshTimer);
	},

	/**
	 * Ferme la connection au serveur
	 * @return {Boolean} True si la connection a ete fermee sinon False
	 */
	close: function() {
		jsocket.core.http.connectedToServer = false;
		return (true);
	},

	/**
	 * Verifie si une commande peut etre envoye au serveur
	 * @return {Boolean} True si la commande peut etre envoyee sinon False
	 */
	checkResponse: function() {
		var now = Math.floor(new Date().getTime() / 1000);
		if (jsocket.core.http.response.waiting == false) {
			return (true);
		} else if ((now - jsocket.core.http.response.lastTime) > jsocket.core.http.response.timeout) {
			jsocket.core.http.response.lastTime = now;
			return (true);
		}
		return (false);
	},

	/**
	 * Envoie les commandes stockees prealablement au serveur.
	 * @return {Boolean} True si les commandes ont ete envoyees sinon False
	 */
	write: function() {
		if (typeof jsocket.core.http.api != 'object' ||
			jsocket.core.http.checkResponse() == false) {
			return (false);
		}
		msg = '';
		if (jsocket.core.http.commands.length > 0) {
			msg = jsocket.core.http.commands.join("\n");
			jsocket.core.http.commands = [ ];
            jsocket.core.http._get(msg + "\n");
		} else {
            jsocket.core.http._get('{"cmd": "refresh", "args": "null", "app": "", "uid": "' +
                                   jsocket.core.http.api.uid + '"}\n');
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
			return (jsocket.core.http.commands.push(msg));
		}
		return (false);
	},

	/**
	 * @event connected
	 * Callback appele par flash lorsque la socket est connectee au serveur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	connected: function() {
		if (typeof jsocket.core.http.api != 'object') {
			return (false);
		}
		jsocket.core.http.connectedToServer = true;
		jsocket.core.http.api.onReceive('{"from": "connect", "value": true}');
		return (true);
	},

	/**
	 * @event disconnected
	 * Callback appele par flash lorsqu'une deconnection a ete effectuee
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	disconnected: function() {
		if (typeof jsocket.core.http.api != 'object') {
			return (false);
		}
		jsocket.core.http.api.parser('{"from": "disconnect", "value": true}');
		jsocket.core.http.connectedToServer = false;
		jsocket.core.http.connect();
		return (true);
	},

	/**
	 * @event receive
	 * Callback appele par socket lors de la reception d'un message
	 * @return {Boolean} True si la commande a ete envoyee a l'API sinon False
	 */
    receive: function() {
        this.parentNode.removeChild(this);
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
