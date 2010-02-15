/**
* Api de dialogue avec JsocketCore.
*/
var jsocketApi = {
	// jsocketCore Object
	core : jsocketCore,
	host : '',
	port : 0,
	debug : false,
	app : [ ],

	/**
	* Connect to the server via jsocketCore
	* @host : hostname or ip destination
	* @port : port destination
	**/
	init : function(host, port) {
		this.host = host;
		this.port = port;
		this.core.api = this;
		this.core.connect(this.host, this.port);
		this.core.send('{"cmd": "connected", "args": "null"}');
	},

	/**
	* Register an application to the API
	* @appName : application name
	* @appObject : optionnal parameter
	**/
	register : function(appName, appObject) {
		var newApp = appObject || { };
		this.app[appName] = newApp;
	},

	/**
	* Appel le callback (s'il existe) d'une application (si elle existe)
	* @appName : application name
	* @callName : Callback name
	* @args : arguments a passer au callback
	**/
	appCallback : function(appName, callName, args) {
		if (typeof(eval('jsocketApi.app["' + appName + '"].' + callName + '(args);')) != 'undefined') {
			eval('jsocketApi.app["' + appName + '"].' + callName + '(args);');
			return (true);
		}
		return (false);
	},

	/**
	* Appel le callback de chaque application
	* @callName : Callback name
	* @args : arguments a passer au callback
	**/
	appCallbacks : function(callName, args) {
		for (var i in this.app) {
			this.appCallback(i, callName, args);
		}
	},

	/**
	* Enable flash console based on debug flag
	* @enable : true or false
	**/
	debug : function(enable) {
		if (enable == true) {
			this.debug = true;
			document.getElementById('flashcontent').style.visibility = 'visible';
		}
		else {
			this.debug = false;
			document.getElementById('flashcontent').style.visibility = 'hidden';
		}
	},

	/**
	* Callback utilise pour transformer du texte en un objet Json
	* @text : le texte a transformer -> string
	**/
	parser : function(text) {
		var data = [];
		var j = json_parse(text);
		if (j.from != null && j.value != null) {
			func_name = j.from.substring(0,1).toUpperCase() + j.from.substring(1, j.from.length);
			if (j.app != null && this.app[j.app] != null) {
				try {
					this.appCallback('on' + func_name, j.value);
				} catch(e) { }
			}
			else {
				try {
					this.appCallbacks('on' + func_name, j.value);
					eval('jsocketApi.on'+func_name+"(jsocketApi.core.stripslashes(j.value))");
				} catch(e) {
					jsocketApi.onError(e);
				}
			}
		}
	},
	
	/**
	* Callback utilise pour recevoir un identifiant par defaut lors de
	* la connection au serveur.
	* @key : identifiant unique de l'utilisateur
	**/
	onConnected : function (key) {
		this.key = key;
	},
	
	/**
	* Callback lorsque la connection avec le serveur est etablie.
	* @code : true ou false
	**/
	onConnect : function (code) {
		//implement onConnect code here.
	},
	
	/**
	* Callback utilise pour recevoir les donnees sortantes du serveur.
	* @message : le message retourne par le serveur -> Json string
	**/
	onReceive : function (message) {
		//implement onReceive code here.
		this.parser(message);
	},
	
	/**
	* Callback lorsque le serveur renvoie des informations suite a l'appel de la fonction auth
	* @code : le retour de l'appel a la methode auth -> bool
	**/
	onAuth : function(code) {
		//implement onAuth code here.
	},
	
	/**
	* Cette fonction permet d'obtenir des droits supplementaire sur le serveur.
	* @appName : le nom de l'application -> string
	* @channel : le nom d'un salon -> string
	* @serveur_syntax : {"cmd": "auth", "args": "passphrase"}
	**/
	auth : function (appName, password) {
		this.core.send('{"cmd": "auth", "args": "'+this.core.addslashes(password)+'", "app": "'+appName+'"}');
	},
	
	/**
	* Callback lorsque le serveur renvoie des informations suite a l'appel de la fonction join
	* @code : le retour de l'appel a la methode join -> bool
	**/
	onJoin : function(code) {
		//implement onJoin code here.
	},
	
	/**
	* Cette fonction permet d'associé le client a un channel sur le serveur.
	* @appName : le nom de l'application -> string
	* @channel : le nom d'un salon -> string
	* @serveur_syntax : {"cmd": "join", "args": "channelName"}
	**/
	join : function(appName, channel) {
		this.core.send('{"cmd": "join", "args": "'+this.core.addslashes(channel)+'", "app": "'+appName+'"}');
	},
	
	/**
	* Callback lorsque le serveur renvoie des informations suite a l'appel de la fonction part
	* @code : le retour de l'appel a la methode part -> bool
	**/
	onPart : function(code) {
		//implement onPart code here.
	},
	
	/**
	* Cette fonction permet de quitter le channel auquel le client est associé.
	* @appName : le nom de l'application -> string
	* @channel : le nom d'un salon -> string
	* @serveur_syntax : {"cmd": "part", "args": "channelName"}
	**/
	part : function(appName, channel) {
		this.core.send('{"cmd": "part", "args": "'+this.core.addslashes(channel)+'", "app": "'+appName+'"}');
	},
	
	/**
	* Callback lorsque le serveur renvoie des informations suite a l'appel de la fonction create
	* @code : le retour de l'appel a la methode create -> bool
	**/
	onCreate : function(code) {
		//implement onCreate code here.
	},
	
	/**
	* Cette fonction permet d'ajouter un nouveau channel sur le serveur.
	* @appName : le nom de l'application -> string
	* @channel : le nom d'un salon -> string
	* @serveur_syntax : {"cmd": "create", "args": "channelName"}
	**/
	create : function(appName, channel) {
		this.core.send('{"cmd": "create", "args": "'+this.core.addslashes(channel)+'", "app": "'+appName+'"}');
	},
	
	/**
	* Callback lorsque le serveur renvoie des informations suite a l'appel de la fonction remove
	* @code : le retour de l'appel a la methode remove -> bool
	**/
	onRemove : function(code) {
		//implement onRemove code here.
	},
	
	/**
	* Cette fonction permet d'effacer un channel du serveur.
	* @appName : le nom de l'application -> string
	* @channel : le nom d'un salon -> string
	* @serveur_syntax : {"cmd": "remove", "args": "channelName"}
	**/
	remove : function(appName, channel) {
		this.core.send('{"cmd": "remove", "args": "'+this.core.addslashes(channel)+'", "app": "'+appName+'"}');
	},
	
	/**
	* Cette fonction permet a un master de forwarder une commande
	* sur tous les clients connectes a son channel
	* @appName : le nom de l'application -> string
	* @command : la commande a forwarder
	**/
	forward : function(appName, command) {
		this.core.send('{"cmd": "forward", "args": "'+this.core.addslashes(command)+'", "app": "'+appName+'"}');
	},
	
	/**
	* Callback appeler lorsque un client recoie un message d'un master
	* @info : [0] = master's username
	*         [1] = commande
	**/
	onForward : function(info) {
		//implement onForward code here.
	},

	/**
	* Permet de lister tous les utilisateurs connecte au channel
	* @channel : nom du channel
	**/
	list : function(channel) {
		this.core.send('{"cmd": "list", "args": "'+this.core.addslashes(channel)+'"}')
	},

	/**
	* Callback appeler contenant la liste des utilisateurs connectes a un channel
	* @tab : liste des utilisateurs
	**/
	onList : function(tab) {
		//implement onList code here.
	},

	/**
	* Envoie un message a un ou plusieurs clients
	* @appName : le nom de l'application -> string
	* @tab : [0] = message a envoyer
	*        [1] = [ '*' ] pour tous les clients du channel
	*              [ '' ] ou [ 'master' ] pour le master du channel
	*              [ 'username1', 'username2', ... ] pour une liste de clients
	**/
	message : function(appName, tab) {
		if (typeof(tab) == 'string') {
			str = tab;
		} else {
			var str = '[ "' + this.core.addslashes(tab[0]) +
				'", [ "' + (tab[1][0] ? this.core.addslashes(tab[1][0]) : '') + '"';
			for (var i = 1; tab[1][i]; ++i) {
				str += (', "' + this.core.addslashes(tab[1][i]) + '"');
			}
			str += ' ]';
		}
		this.core.send('{"cmd": "message", "app": "'+appName+'", "args": ' + str + '}');
	},

	/**
	* Callback reception d'un message
	* @command : [0] = l'emmeteur du message
	*            [1] = le message
	**/
	onMessage : function(command) {
		//implement onMessage code here.
	},

	/**
	* Callback sur l'erreur d'execution d'une des methodes de l'api
	* @error : le message d'erreur -> string
	**/
	onError : function(error) {
		alert(error);
	}
};