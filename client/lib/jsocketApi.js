/**
* Api de dialogue avec JsocketCore.
*/
var jsocketApi = {
	// jsocketCore Object
	core : "",
	
	/**
	* Callback utilise pour transformer du texte en un objet Json
	* @text : le texte a transformer -> string
	**/
	parser : function(text) {
		var data = [];
		var j = json_parse(text);
		if (j.cmd != null && j.args != null) {
			func_name = j.cmd.substring(0,1).toUpperCase() + j.cmd.substring(1, j.cmd.length)
			try {
				eval('jsocketApi.on'+func_name+"('"+j.args+"')");
			} catch(e) {
				jsocketApi.onError(e);
			}
		}
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
		alert(code);
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
	* Callback sur l'erreur d'execution d'une des methodes de l'api
	* @error : le message d'erreur -> string
	**/
	onError : function(error) {
		alert(error);
	}
};