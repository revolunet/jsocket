/**
 * @class jsocket.api
 * <p><b><u>jsocket API</u></b></p>
 * <p>Chaque callback est appele avec en parametres un dictionnaire comprenant les attributs
 * suivants:
 * <div class="mdetail-params"><ul>
 * <li><b><tt>param.value: value JSON field (empty string '' if not exists)</tt></b></li>
 * <li><b><tt>param.app: app JSON field (empty string '' if not exists)</tt></b></li>
 * <li><b><tt>param.channel: channel JSON field (empty string '' if not exists)</tt></b></li>
 * </ul></div></p>
 *
 * <p><b><u>Exemple:</u></b></p>
<pre><code>
jsocket.api.app['myapp'].onJoin(args) {
  args.value = true;
  args.app = 'myapp';
  args.channel = 'myapp_channel';
};
</code></pre>
 * @author Revolunet
 * @version 0.2.6
 * @singleton
 */
jsocket.api = {
	/**
	 * Le core a utiliser par defaut
	 * @private
	 * @type Object
	 */
	core: null,

	/**
	 * A activer pour afficher les commandes JSON en entree/sortie
	 * @private
	 * @type Boolean
	 */
	debug: false,

	/**
	 * Le tableau des applications enregistrees dans l'API
	 * @private
	 * @type Array
	 */
	app: [ ],

	/**
	 * L'uid du client une fois connecte
	 * @public
	 * @type String
	 */
	uid: '',

	/**
	 * La liste des commandes en attente d'envoie
	 * @private
	 * @type Array
	 */
	commands: [ ],

	/**
	 * La liste des cores disponibles.
	 * Si un core ne fonctionne pas, alors
	 * le core suivant est teste.
	 * @private
	 * @type Object
	 */
	cores: {
		tcp: {
			object: jsocket.core.tcp,
			tested: false,
			worked: true
		},
		http: {
			object: jsocket.core.http,
			tested: false,
			worked: true
		},
		websocket: {
			object: jsocket.core.websocket,
			tested: false,
			worked: true
		}
	},

	/**
	 * <p>Parametres de configuration:</p>
	 * <p><div class="mdetail-params"><ul>
	 * <li><b><tt>tcp.host: Host pour le core {@link jsocket.core.tcp#loaded}</tt></b></li>
	 * <li><b><tt>tcp.port: Port pour le core {@link jsocket.core.tcp#loaded}</tt></b></li>
	 * <li><b><tt>http.url: Url pour le core {@link jsocket.core.http#loaded}</tt></b></li>
	 * <li><b><tt>http.refreshTimer: Temps entre chaque rafraichissement (en ms) pour le core {@link jsocket.core.http#loaded}</tt></b></li>
	 * <li><b><tt>websocket.host: Host pour le core {@link jsocket.core.websocket#loaded}</tt></b></li>
	 * <li><b><tt>websocket.port: Port pour le core {@link jsocket.core.websocket#loaded}</tt></b></li>
	 * </ul></div></p>
	 * Ce parametre peut etre changer directement comme dans l'exemple ci-dessous
	 * ou via la methode {@link jsocket.api.configure}
	 * <p><b><u>Exemple de configuration:</u></b></p>
<pre><code>
jsocket.api.settings = {
  tcp: {
    host: 'localhost',
	port: 8080
  },
  http: {
    url: 'http://localhost:8081/',
	refreshTimer: 1000
  },
  websocket: {
    host: 'localhost',
    port: 8082
  }
  ,vhost:'test.quickprez.com'
};
</code></pre>
	 */
	settings: {
		tcp: {
			host: 'localhost',
			port: 8080
		},
		http: {
			url: 'http://localhost:8081/',
			refreshTimer: 1000
		},
		websocket: {
			host: 'localhost',
			port: 8082
		},
        vhost:''
	},

	/**
	 * <p>Connection au serveur via le jsocket.core</p>
	 * @param {Object} Parametre optionnel de configuration {@link jsocket.api.settings}
	 */
	connect: function(settings) {
		if (typeof settings != undefined && settings != null) {
			jsocket.api.configure(settings);
		}
		if (jsocket.api.core == null) {
			jsocket.api.setCore();
		}
		jsocket.api.core.api = this;
		jsocket.api.core.connect();
	},

	/**
	 * <p>Permet de changer la configuration de l'api</p>
	 * <p>La configuration donnee en parametre peut etre partielle mais doit
	 * tout de meme respecter l'arborescence de {@link jsocket.api.settings}<p>
	 * @param {Object} Configuration {@link jsocket.api.settings}
	 */
	configure: function(settings) {
		for (core in jsocket.api.settings) {
			if (typeof settings[core] == 'object') {
				for (opt in jsocket.api.settings[core]) {
					if (typeof settings[core][opt] != 'undefined') {
						jsocket.api.settings[core][opt] = settings[core][opt];
					}
				}
			}
            else if (typeof settings[core] == 'string') {
                jsocket.api.settings[core] = settings[core];
            }
		}
        console.log('new settings: ', jsocket.api.settings);
	},

	/**
	 * Selectionne un core
	 * @private
	 */
	setCore: function() {
		jsocket.api.method(jsocket.core.websocket);
	},

	/**
	 * <p>Deconnection du server via le core en cours.</p>
	 * @return {Boolean} True si la deconnection a reussie sinon False
	 */
	disconnect: function() {
		if (jsocket.api.core != null) {
			return (jsocket.api.core.close());
		}
		return (false);
	},

	/**
	 * <p>Changement de la methode de contact pour le serveur (par defaut TCP).</p>
	 *
	 * <p>Cores disponibles:
	 * <div class="mdetail-params"><ul>
	 * <li><b><tt>{@link jsocket.core.tcp#loaded}</tt></b></li>
	 * <li><b><tt>{@link jsocket.core.http#loaded}</tt></b></li>
	 * <li><b><tt>{@link jsocket.core.websocket#loaded}</tt></b></li>
	 * </ul></div></p>
	 * @param {Object} newCore La variable contenant le nouveau jsocketCore (tcp, http, websocket)
	 */
	method: function(newCore) {
		if (jsocket.api.core != null) {
			jsocket.api.disconnect();
			jsocket.api.uid = '';
			jsocket.api.core.isWorking = false;
			jsocket.api.core = newCore;
			jsocket.api.core.isWorking = true;
			jsocket.api.core.api = this;
			jsocket.api.core.connect();
		} else {
			jsocket.api.core = newCore;
			jsocket.api.core.isWorking = true;
			jsocket.api.core.api = this;
		}
	},

	/**
	 * <p>Enregistre une application dans l'API</p>
	 *
	 * <p><b><u>Exemple d'utilisation:</u></b></p>
<pre><code>
var myApplication = {
  onConnected: function(data) {
    if (data.value == true) {
	  alert('Vous etes connecte !');
	} else {
	  alert('La connection au serveur a echoue');
	}
  }
};
jsocket.api.register('myApplicationName', myApplication);
</code></pre>
	 * @param {String} appName Le nom de l'application
	 * @param {Object} appObject L'application contenant les callbacks
	 */
	register: function(appName, appObject) {
		var newApp = appObject || { };
		jsocket.api.app[appName] = newApp;
		jsocket.api.app[appName].isMaster = false;
		if (typeof jsocket.api.app[appName].onHistory == 'undefined') {
			jsocket.api.app[appName].onHistory = jsocket.api.onHistory;
		}
	},

	/**
	 * @private
	 * Test si une application existe
	 * @param {String} appName Le nom de l'application
	 * @return {Boolean} True si l'application exists sinon False
	 */
	appExists: function(appName) {
		if (typeof(jsocket.api.app[appName]) != 'undefined') {
			return (true);
		}
		return (false);
	},

	/**
	 * @private
	 * Appel le callback (s'il existe) d'une application (si elle existe)
	 * @param {String} appName Le nom de l'application
	 * @param {String} callName Le nom du callback
	 * @return {Boolean} True si le callback a ete appele sinon False
	 */
	appCallback: function(appName, callName, args) {
		if (typeof(eval('jsocket.api.app["' + appName + '"].' + callName)) != 'undefined') {
			eval('jsocket.api.app["' + appName + '"].' + callName + '(args);');
			return (true);
		}
		return (false);
	},

	/**
	 * @private
	 * Appel le callback de chaque application
	 * @param {String} callName Le nom du callback
	 * @param {Mixed} args Les arguments a passer au callback
	 */
	appCallbacks: function(callName, args) {
		for (var i in jsocket.api.app) {
			jsocket.api.appCallback(i, callName, args);
		}
	},

	/**
	 * Active la console de debug de flash
	 * @param {Boolean} enable True pour activer la console False pour desactiver
	 */
	debug: function(enable) {
		if (jsocket.api.core.initialized == false) {
			setTimeout("jsocket.api.debug(" + enable + ");", 1000);
			return (false);
		}
		if (enable == true) {
			jsocket.api.debug = true;
			document.getElementById('socketBridge').style.top = '0px';
		}
		else {
			jsocket.api.debug = false;
			document.getElementById('socketBridge').style.top = '-1000px';
		}
	},

	/**
	 * @private
	 * Callback utilise pour transformer du texte en un objet JSON
	 * @param {String} text Le texte a transformer
	 */
	parser: function(text) {
		var j = { };
		try {
			j = JSON.parse(text);
		} catch(e) {
			return (false);
		}
		if (j.from != null && j.value != null) {
			func_name = j.from.substring(0, 1).toUpperCase() + j.from.substring(1, j.from.length);
			var args = { };
			args.value = (j.value != null ? j.value: '');
			args.channel = (j.channel != null ? j.channel: '');
			args.app = (j.app != null ? j.app: '');
			if (j.from == 'history') {
				args.channel = decodeURIComponent(args.channel.replace(/%27/g, "'"));
				args.app = decodeURIComponent(args.app.replace(/%27/g, "'"));
			} else {
				args = jsocket.api.core.stripslashes(args);
			}
			if (j.app != null && j.app.length > 0 &&
				jsocket.api.appExists(j.app) == true) {
				try {
					jsocket.api.appCallback(args['app'], 'on' + func_name, args);
				} catch(e) {
					return (false);
				}
			}
			else {
				try {
					jsocket.api.appCallbacks('on' + func_name, args);
					eval('jsocket.api.on' + func_name + "(args)");
				} catch(e) {
					return (jsocket.api.onError(e));
				}
			}
		}
	},

	/**
	 * @private
	 * @event onConnected
	 * Callback utilise pour recevoir un identifiant par defaut lors de
	 * la connection au serveur.
	 * @param {Object} args Tableau contenant l'identifiant unique de l'utilisateur
	 */
	onConnected: function(args) {
		jsocket.api.uid = args.value;
		jsocket.api.sendPool();
	},

	/**
	 * @event onDisconnect
	 * Callback appele via flash quand la connection avec le serveur echoue
	 * @param {Object} args Objet ayant pour <i>value</i> un Boolean
	 */
	onDisconnect: function(args) {
	},

	/**
	 * @event onConnect
	 * Callback lorsque la connection avec le serveur est etablie.
	 * @param {Object} args Objet ayant pour <i>value</i> un Boolean
	 */
	onConnect: function(args) {
	},

	/**
	 * @private
	 * @event onReceive
	 * Callback utilise pour recevoir les donnees sortantes du serveur.
	 * @param {String} message Le message retourne par le serveur contenant une ou
	 * plusieurs commandes JSON. (Si plusieurs, elle sont alors separees par des \n)
	 */
	onReceive: function(message) {
		//console.log('jsocket.api.receive: ', message);
		jsocket.api.parser(message);
	},

	/**
	 * @event onStatus
	 * Callback appele pour le master d'un channel lorsqu'un utilisateur
	 * quitte ou rejoind le channel.
	 * @param {Object} args Objet
	 */
	onStatus: function(args) {
	},

	/**
	 * @event onAuth
	 * Callback lorsque le serveur renvoie des informations suite a l'appel de la fonction auth
	 * @param {Object} args Objet ayant pour value le retour de l'appel a la methode auth
	 */
	onAuth: function(args) {
	},

	/**
	 * Cette fonction permet d'obtenir des droits supplementaire sur le serveur.
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 * @param {String} password Le mot de passe pour passer admin sur le serveur
	 */
	auth: function(appName, channel, password) {
		if (typeof(eval('jsocket.api.app["' + appName + '"]')) != 'undefined') {
			jsocket.api.app[appName].isMaster = true;
		}
		var json = {
			cmd: 'auth',
			args: password,
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * Authentifie un utilisateur (comme master) sur un channel
	 * @param {String} appName Le nom de l'application/channel
	 * @param {String} channel Le nom d'un salon
	 * @param {String} password Le mot de passe du channel
	 */
	chanAuth: function(appName, channel, password) {
		if (typeof(eval('jsocket.api.app["' + appName + '"]')) != 'undefined') {
			jsocket.api.app[appName].isMaster = true;
		}
		var json = {
			cmd: 'chanAuth',
			args: password,
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onChanAuth
	 * Callback lorsque le serveur renvoie des informations suite a l'appel de la fonction chanAuth
	 * @param {Object} args Channel password or false
	 */
	onChanAuth: function(args) {
	},

	/**
	 * @event onJoin
	 * Callback lorsque le serveur renvoie des informations suite a l'appel de la fonction join
	 * @param {Object} args Le retour de l'appel a la methode join
	 */
	onJoin: function(args) {
	},

	/**
	 * Cette fonction permet d'associé le client a un channel sur le serveur.
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 * @param {String} password Le mot de passe du salon
	 */
	join: function(appName, channel, password) {
		var json = {
			cmd: 'join',
			args: [ channel, password ],
			channel: channel,
			app: appName,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onPart
	 * Callback lorsque le serveur renvoie des informations suite a l'appel de la fonction part
	 * @param {Object} args Le retour de l'appel a la methode part
	 */
	onPart: function(args) {
	},

	/**
	 * Cette fonction permet de quitter le channel auquel le client est associé.
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 */
	part: function(appName, channel) {
		var json = {
			cmd: 'part',
			args: channel,
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onCreate
	 * Callback lorsque le serveur renvoie des informations suite a l'appel de la fonction create
	 * @param {Object} args Le retour de l'appel a la methode create
	 */
	onCreate: function(args) {
	},

	/**
	 * Cette fonction permet d'ajouter un nouveau channel sur le serveur.
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 * @param {String} password Le mot de passe du salon
	 */
	create: function(appName, channel, password) {
		if (typeof(eval('jsocket.api.app["' + appName + '"]')) != 'undefined') {
			jsocket.api.app[appName].isMaster = true;
		}
		var json = {
			cmd: 'create',
			args: [ channel, password ],
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onRemove
	 * Callback lorsque le serveur renvoie des informations suite a l'appel de la fonction remove
	 * @param {Object} args Le retour de l'appel a la methode remove
	 */
	onRemove: function(args) {
	},

	/**
	 * Cette fonction permet d'effacer un channel du serveur.
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 */
	remove: function(appName, channel) {
		var json = {
			cmd: 'remove',
			args: channel,
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * Change le nom de l'utilisateur courant
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 * @param {String} nickname Le nom d'utilisateur
	 */
	nick: function(appName, channel, nickname) {
		var json = {
			cmd: 'nick',
			args: nickname,
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onNick
	 * Callback lorsque le serveur renvoie des informations suite a
	 * l'appel de la fonction {@link #nick nick}
	 * @param {Object} args Le retour de l'appel a la methode {@link #nick nick}
	 */
	onNick: function(args) {
	},

	/**
	 * Cette fonction permet a un master de forwarder une commande
	 * sur tous les clients connectes a son channel
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 * @param {String} command La commande a forwarder
	 */
	forward: function(appName, channel, command) {
		var json = {
			cmd: 'forward',
			args: command,
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onForward
	 * Callback appeler lorsque un client recoie un message d'un master
	 * (via {@link #forward forward})
	 * @param {Object} args Le retour de la commande {@link #forward forward}
	 */
	onForward: function(args) {
	},

	/**
	 * Permet de lister tous les utilisateurs connecte au channel
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 */
	list: function(appName, channel) {
		var json = {
			cmd: 'list',
			args: channel,
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onList
	 * Callback appeler contenant la liste des utilisateurs connectes a un channel
	 * @param {Object} args Le retour de la commande {@link #list list}
	 */
	onList: function(args) {
	},

	/**
	 * Demande au serveur la liste des dernieres commandes effectuees par le master.
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 */
	history: function(appName, channel) {
		var json = {
			cmd: 'history',
			args: 'null',
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onHistory
	 * <p>Callback appeler contenant la liste des dernieres commandes effectuees par le master.
	 * Toutes les commandes recues en value seront alors repassee au parser de l'API (et donc
	 * les callbacks du client correspondant aux commandes seront rappeles).</p>
	 * <p>Si par defaut une interface n'a pas cet evenement d'implementer, c'est celui de l'API
	 * qui lui sera affectee.</p>
	 * @param {Object} args Le retour de la commande {@link #history history}
	 */
	onHistory: function(args) {
		var values = args.value;
		var length = values.length;
		if (!(typeof values == 'object' && length > 0)) {
			return (false);
		}
		for (var i in values) {
			if (typeof values[i]['json'] != 'undefined') {
				var cmd = values[i]['json'].replace(/\%27/g, "'");
				cmd = decodeURIComponent(cmd);
				jsocket.api.parser(cmd);
			}
		}
	},

	/**
	 * Envoie un message a un ou plusieurs clients
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 * @param {Object} tab [0] = message a envoyer
	 *        [1] = [ '*' ] pour tous les clients du channel
	 *              [ '' ] ou [ 'master' ] pour le master du channel
	 *              [ 'username1', 'username2', 'uidClient3', ... ] pour une liste de clients
	 */
	message: function(appName, channel, tab) {
		var json = {
			cmd: 'message',
			args: tab,
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onMessage
	 * Callback reception d'un message {@link #message message}
	 * @param {Object} args command [0] = l'emmeteur du message
	 *        [1] = le message
	 */
	onMessage: function(args) {
	},

	/**
	 * Renvoie le statut de l'utilisateur courant
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 */
	getStatus: function(appName, channel) {
		var json = {
			cmd: 'getStatus',
			args: 'null',
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onGetStatus
	 * Callback reception status {@link #getStatus getStatus}
	 * @param {Object} args Status de l'utilisateur courant
	 */
	onGetStatus: function(args) {
	},

	/**
	 * Remplace le status de l'utilisateur courant
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 * @param {String} status Le status de l'utilisateur
	 */
	setStatus: function(appName, channel, status) {
		var json = {
			cmd: 'setStatus',
			args: status,
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onSetStatus
	 * Callback de la commande {@link #setStatus setStatus}
	 * @param {Object} args True or false
	 */
	onSetStatus: function(args) {
	},

	/**
	 * Renvoie l'heure a laquelle l'utilisateur courant s'est connecte
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 */
	timeConnect: function(appName, channel) {
		var json = {
			cmd: 'timeConnect',
			args: 'null',
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onTimeConnect
	 * Callback de la commande {@link #timeConnect timeConnect}
	 * @param {Object} args True or False
	 */
	onTimeConnect: function(args) {
	},

	/**
	 * Change le mot de passe d'un salon
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 * @param {String} password Le mot de passe
	 */
	chanMasterPwd: function(appName, channel, password) {
		var json = {
			cmd: 'chanMasterPwd',
			args: password,
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onChanMasterPwd
	 * Callback {@link #chanMasterPwd chanMasterPwd}
	 * @param {Object} args True or false
	 */
	onChanMasterPwd: function(args) {
	},

	/**
	 * @event onError
	 * Callback sur l'erreur d'execution d'une des methodes de l'API
	 * @param {String} error Le message d'erreur
	 */
	onError: function(error) {
		//console.log('jsocket.api.onError: ', error);
		jsocket.api.method(jsocket.core.websocket);
		jsocket.api.connect();
	},

	/**
	 * @private
	 * @event onWebSocketError
	 * Callback sur l'erreur venant du core WebSocket. On change
	 * alors la methode de dialogue avec le serveur par TCP.
	 */
	onWebSocketError: function() {
		if (jsocket.core.tcp.isWorking == false) {
			jsocket.api.method(jsocket.core.tcp);
			jsocket.api.connect();
		}
	},

	/**
	 * @private
	 * @event onTCPError
	 * Callback sur l'erreur venant du core TCP. On change alors
	 * la methode de dialogue avec le serveur par HTTP.
	 * @param {String} error Le message d'erreur
	 */
	onTCPError: function(error) {
		if (jsocket.core.http.isWorking == false) {
			jsocket.api.method(jsocket.core.http);
			jsocket.api.connect();
		}
	},

	/**
	 * @private
	 * Une fois que le client recupere son uid, alors les commandes
	 * en queue sont envoyes au serveur.
	 */
	sendPool: function() {
		for (var i = 0; i < jsocket.api.commands.length; ++i) {
			//console.log('jsocket.api.send: ', jsocket.api.commands[i].replace(/jsocket\.api\.uid/, jsocket.api.uid));
			jsocket.api.core.send(jsocket.api.commands[i].replace(/jsocket\.api\.uid/, jsocket.api.uid));
		}
		jsocket.api.commands = [ ];
	},

	/**
	 * Gestion de queue pour les commandes a envoyer.
	 * Si jsocket.api.uid est null/empty alors on stock les
	 * commands puis on les envoie lorsque l'uid est renseigne.
	 * @param {String} msg Le message (commande JSON) a envoyer
	 */
	send: function(msg) {
		if (jsocket.api.uid != '') {
			//console.log('jsocket.api.send: ', msg.replace(/jsocket\.api\.uid/, jsocket.api.uid));
			jsocket.api.core.send(msg.replace(/jsocket\.api\.uid/, jsocket.api.uid));
		} else if (jsocket.api.commands.length < 10) {
			jsocket.api.commands.push(msg);
		}
	}
};
