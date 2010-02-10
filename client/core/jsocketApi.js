/**
* Api de dialogue avec JsocketCore.
*/
var jsocketApi = {
	// jsocketCore Object
	core : jsocketCore,
	host : '',
	port : 0,
	debug : false,

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
			func_name = j.from.substring(0,1).toUpperCase() + j.from.substring(1, j.from.length)
			try {
				eval('jsocketApi.on'+func_name+"(j.value)");
			} catch(e) {
				jsocketApi.onError(e);
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
	* @channel : le nom d'un salon -> string
	* @serveur_syntax : {"cmd": "auth", "args": "passphrase"}
	**/
	auth : function (password) {
		this.core.send('{"cmd": "auth", "args": "'+password+'"}');
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
	* @channel : le nom d'un salon -> string
	* @serveur_syntax : {"cmd": "join", "args": "channelName"}
	**/
	join : function(channel) {
		this.core.send('{"cmd": "join", "args": "'+channel+'"}');
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
	* @channel : le nom d'un salon -> string
	* @serveur_syntax : {"cmd": "part", "args": "channelName"}
	**/
	part : function(channel) {
		this.core.send('{"cmd": "part", "args": "'+channel+'"}');
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
	* @channel : le nom d'un salon -> string
	* @serveur_syntax : {"cmd": "create", "args": "channelName"}
	**/
	create : function(channel) {
		this.core.send('{"cmd": "create", "args": "'+channel+'"}');
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
	* @channel : le nom d'un salon -> string
	* @serveur_syntax : {"cmd": "remove", "args": "channelName"}
	**/
	remove : function(channel) {
		this.core.send('{"cmd": "remove", "args": "'+channel+'"}');
	},
	
	/**
	* Cette fonction permet a un master de forwarder une commande
	* sur tous les clients connectes a son channel
	* @command : la commande a forwarder
	**/
	forward : function(command) {
		this.core.send('{"cmd": "forward", "args": "'+command+'"}');
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
	* Callback sur l'erreur d'execution d'une des methodes de l'api
	* @error : le message d'erreur -> string
	**/
	onError : function(error) {
		alert(error);
	}
};