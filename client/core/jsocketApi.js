/**
* Api de dialogue avec JsocketCore.
*  Callback return args:
*   - tab['value']: value JSON field (empty string '' if not exists)
*   - tab['app'] : app JSON field (empty string '' if not exists)
*   - tab['channel'] : channel JSON field (empty string '' if not exists)
*  Example:
*   jsocketApi.app['myapp'].onJoin(args) {
*		//args['value'] = true
*		//args['app'] = 'myapp'
*		//args['channel'] = 'myapp_channel'
*	};
**/
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
		jsocketApi.host = host;
		jsocketApi.port = port;
		jsocketApi.core.api = this;
		jsocketApi.core.connect(jsocketApi.host, jsocketApi.port);
		jsocketApi.core.send('{"cmd": "connected", "args": "null", "app": ""}');
	},

	/**
	* Register an application to the API
	* @appName : application name
	* @appObject : optionnal parameter
	**/
	register : function(appName, appObject) {
		var newApp = appObject || { };
		jsocketApi.app[appName] = newApp;
		jsocketApi.app[appName].isMaster = false;
	},

	/**
	* Appel le callback (s'il existe) d'une application (si elle existe)
	* @appName : application name
	* @callName : Callback name
	* @args : arguments a passer au callback
	**/
	appCallback : function(appName, callName, args) {
		if (typeof(eval('jsocketApi.app["' + appName + '"].' + callName)) != 'undefined') {
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
		for (var i in jsocketApi.app) {
			jsocketApi.appCallback(i, callName, args);
		}
	},

	/**
	* Enable flash console based on debug flag
	* @enable : true or false
	**/
	debug : function(enable) {
		if (jsocketApi.core.initialized == false) {
			setTimeout("jsocketApi.debug(" + enable + ");", 1000);
			return (false);
		}
		if (enable == true) {
			jsocketApi.debug = true;
			document.getElementById('socketBridge').width = '900px';
			document.getElementById('socketBridge').height = '250px';
		}
		else {
			jsocketApi.debug = false;
			document.getElementById('socketBridge').width = '1px';
			document.getElementById('socketBridge').height = '1px';
		}
	},

	/**
	* Callback utilise pour transformer du texte en un objet Json
	* @text : le texte a transformer -> string
	**/
	parser : function(text) {
		var j = json_parse(text);
		if (j.from != null && j.value != null) {
			func_name = j.from.substring(0,1).toUpperCase() + j.from.substring(1, j.from.length);
			var args = { };
			args.value = (j.value != null ? j.value : '');
			args.channel = (j.channel != null ? j.channel : '');
			args.app = (j.app != null ? j.app : '');
			args = jsocketApi.core.stripslashes(args);
			if (j.app != null) {
				try {
					jsocketApi.appCallback(args['app'], 'on' + func_name, args);
				} catch(e) { }
			}
			else {
				try {
					jsocketApi.appCallbacks('on' + func_name, args);
					eval('jsocketApi.on'+func_name+"(args)");
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
		jsocketApi.key = key;
	},
	
	/**
	* Callback appele via flash quand la connection avec le serveur echoue
	* @code : true or false
	**/
	onDisconnect : function (code) {
		//implement onDisconnect code here.
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
		jsocketApi.parser(message);
	},
	
	/**
	* Callback appele pour le master d'un channel lorsqu'un utilisateur
	* quit ou rejoind le channel.
	* @tab : [0] Nom du client
	*        [1] Status (online, offline)
	**/
	onStatus : function (tab) {
		//implement onStatus code here.
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
	* @password : mot de passe pour passer admin sur le serveur -> string
	**/
	auth : function (appName, channel, password) {
		if (typeof(eval('jsocketApi.app["' + appName + '"]')) != 'undefined') {
			jsocketApi.app[appName].isMaster = true;
		}
		appName = jsocketApi.core.addslashes(appName);
		channel = jsocketApi.core.addslashes(channel);
		password = jsocketApi.core.addslashes(password);
		jsocketApi.core.send('{"cmd": "auth", "args": "'+password+'", "app": "'+appName+'", "channel": "'+channel+'"}');
	},
	
	/**
	* Authentifie un utilisateur (comme master) sur un channel
	* @appName : le nom de l'application/channel -> string
	* @channel : le nom d'un salon -> string
	* @password : le mot de passe du channel -> string
	**/
	chanAuth : function (appName, channel, password) {
		if (typeof(eval('jsocketApi.app["' + appName + '"]')) != 'undefined') {
			jsocketApi.app[appName].isMaster = true;
		}
		appName = jsocketApi.core.addslashes(appName);
		channel = jsocketApi.core.addslashes(channel);
		password = jsocketApi.core.addslashes(password);
		jsocketApi.core.send('{"cmd": "chanAuth", "args": "'+password+'", "app": "'+appName+'", "channel": "'+channel+'"}');
	},
	
	/**
	* Callback lorsque le serveur renvoie des informations suite a l'appel de la fonction chanAuth
	* @code : channel password or false
	**/
	onChanAuth : function (code) {
		//implement onChanAuth code here.
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
	* @password : le mot de passe du salon -> string
	* @serveur_syntax : {"cmd": "join", "args": "channelName"}
	**/
	join : function(appName, channel, password) {
		appName = jsocketApi.core.addslashes(appName);
		channel = jsocketApi.core.addslashes(channel);
		password = jsocketApi.core.addslashes(password);
		jsocketApi.core.send('{"cmd": "join", "args": [ "'+channel+'", "'+password+'" ], "channel": "'+channel+'", "app": "'+appName+'"}');
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
		appName = jsocketApi.core.addslashes(appName);
		channel = jsocketApi.core.addslashes(channel);
		jsocketApi.core.send('{"cmd": "part", "args": "'+channel+'", "app": "'+appName+'", "channel": "'+channel+'"}');
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
	* @password : mot de passe du salon -> string
	* @serveur_syntax : {"cmd": "create", "args": "channelName"}
	**/
	create : function(appName, channel, password) {
		if (typeof(eval('jsocketApi.app["' + appName + '"]')) != 'undefined') {
			jsocketApi.app[appName].isMaster = true;
		}
		appName = jsocketApi.core.addslashes(appName);
		channel = jsocketApi.core.addslashes(channel);
		password = jsocketApi.core.addslashes(password);
		jsocketApi.core.send('{"cmd": "create", "args": [ "'+channel+'", "'+password+'" ], "app": "'+appName+'", "channel": "'+channel+'"}');
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
		appName = jsocketApi.core.addslashes(appName);
		channel = jsocketApi.core.addslashes(channel);
		jsocketApi.core.send('{"cmd": "remove", "args": "'+channel+'", "app": "'+appName+'", "channel": "'+channel+'"}');
	},
	
	/**
	* Change le nom d'utilisateur
	* @appName : le nom de l'application -> string
	* @channel : le nom d'un salon -> string
	* @nickname : le nom d'utilisateur
	**/
	nick : function(appName, channel, nickname) {
		appName = jsocketApi.core.addslashes(appName);
		channel = jsocketApi.core.addslashes(channel);
		nickname = jsocketApi.core.addslashes(nickname);
		jsocketApi.core.send('{"cmd": "nick", "args": "'+nickname+'", "app": "'+appName+'", "channel": "'+channel+'"}');
	},
	
	/**
	* Callback lorsque le serveur renvoie des informations suite a l'appel de la fonction nick
	* @code : le retour de l'appel a la methode nick -> bool
	**/
	onNick : function(code) {
		//implement onNick code here.
	},
	
	/**
	* Cette fonction permet a un master de forwarder une commande
	* sur tous les clients connectes a son channel
	* @appName : le nom de l'application -> string
	* @channel : le nom d'un salon -> string
	* @command : la commande a forwarder
	**/
	forward : function(appName, channel, command) {
		appName = jsocketApi.core.addslashes(appName);
		channel = jsocketApi.core.addslashes(channel);
		command = jsocketApi.core.addslashes(command);
		jsocketApi.core.send('{"cmd": "forward", "args": "'+command+'", "app": "'+appName+'", "channel": "'+channel+'"}');
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
	* @appName : le nom de l'application -> string
	* @channel : le nom d'un salon -> string
	**/
	list : function(appName, channel) {
		appName = jsocketApi.core.addslashes(appName);
		channel = jsocketApi.core.addslashes(channel);
		jsocketApi.core.send('{"cmd": "list", "args": "'+channel+'", "app": "'+appName+'", "channel": "'+channel+'"}')
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
	* @channel : le nom d'un salon -> string
	* @tab : [0] = message a envoyer
	*        [1] = [ '*' ] pour tous les clients du channel
	*              [ '' ] ou [ 'master' ] pour le master du channel
	*              [ 'username1', 'username2', ... ] pour une liste de clients
	**/
	message : function(appName, channel, tab) {
		if (typeof(tab) == 'string') {
			str = jsocketApi.core.addslashes(tab);
		} else {
			var str = '[ "' + jsocketApi.core.addslashes(tab[0]) +
				'", [ "' + (tab[1][0] ? jsocketApi.core.addslashes(tab[1][0]) : '') + '"';
			for (var i = 1; tab[1][i]; ++i) {
				str += (', "' + jsocketApi.core.addslashes(tab[1][i]) + '"');
			}
			str += ' ] ]';
		}
		appName = jsocketApi.core.addslashes(appName);
		channel = jsocketApi.core.addslashes(channel);
		jsocketApi.core.send('{"cmd": "message", "app": "'+appName+'", "args": ' + str + ', "channel": "'+channel+'"}');
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
	* Renvoie le statut de l'utilisateur courant
	* @appName : le nom de l'application -> string
	* @channel : le nom d'un salon -> string
	**/
	getStatus : function(appName, channel) {
		appName = jsocketApi.core.addslashes(appName);
		channel = jsocketApi.core.addslashes(channel);
		jsocketApi.core.send('{"cmd": "getStatus", "args": "null", "app": "'+appName+'", "channel": "'+channel+'"}');
	},

	/**
	* Callback reception status
	* @status : status de l'utilisateur courant
	**/
	onGetStatus : function(status) {
		//implement onGetStatus code here.
	},
	
	/**
	* Set le status d'un utilisateur
	* @appName : le nom de l'application -> string
	* @channel : le nom d'un salon -> string
	* @status : le status de l'utilisateur
	**/
	setStatus : function(appName, channel, status) {
		appName = jsocketApi.core.addslashes(appName);
		channel = jsocketApi.core.addslashes(channel);
		status = jsocketApi.core.addslashes(status);
		jsocketApi.core.send('{"cmd": "setStatus", "args": "'+status+'", "app": "'+appName+'", "channel": "'+channel+'"}');
	},

	/**
	* Callback setStatus
	* @code : true or false
	**/
	onSetStatus : function(code) {
		//implement onSetStatus code here.
	},

	/**
	* Renvoie l'heure a laquelle l'utilisateur courant s'est connecte
	* @appName : le nom de l'application -> string
	* @channel : le nom d'un salon -> string
	**/
	timeConnect : function(appName, channel) {
		appName = jsocketApi.core.addslashes(appName);
		channel = jsocketApi.core.addslashes(channel);
		jsocketApi.core.send('{"cmd": "timeConnect", "args": "null", "app": "'+appName+'", "channel": "'+channel+'"}');
	},

	/**
	* Callback timeConnect
	* @code : true or false
	**/
	onTimeConnect : function(code) {
		//implement onSetStatus code here.
	},

	/**
	* Change le mot de passe d'un salon
	* @appName : le nom de l'application -> string
	* @channel : le nom d'un salon -> string
	* @password : mot de passe -> string
	**/
	chanMasterPwd : function(appName, channel, password) {
		appName = jsocketApi.core.addslashes(appName);
		channel = jsocketApi.core.addslashes(channel);
		password = jsocketApi.core.addslashes(password);
		jsocketApi.core.send('{"cmd": "chanMasterPwd", "args": "'+password+'", "app": "'+appName+'", "channel": "'+channel+'"}');
	},

	/**
	* Callback chanMasterPwd
	* @code : true or false
	**/
	onChanMasterPwd : function(code) {
		//implement onSetStatus code here.
	},

	/**
	* Callback sur l'erreur d'execution d'une des methodes de l'api
	* @error : le message d'erreur -> string
	**/
	onError : function(error) {
		alert(error);
	}
};