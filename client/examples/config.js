//
// sample config to connect to a room
//
// NOTE: the room must have been creted before

var jsocketConfig = {
	"ROOM": "mychannel",
	// id of the room we want to connect
	// "ROOM_ID": "1882", 
	// password to access the room
	"ROOM_PWD": "9088",
	// password to control the room
	"ROOM_CTRLPASS": "383033", 
	// 
	//"VHOST": "http://beta.quickprez.com", 
	//"JSAPI": "http://api.jsocket.com/prod/jsocket-min.js", 
	//
	// jsocket server config
	"SERVER": "127.0.0.1", 
	"SERVER_WEBSOCKET_PORT": 8080, 
	// for the polling
	"URL_FAILOVER": "http://127.0.0.1:81", 
	"SWF_URI": "http://beta.quickprez.com/apps/whiteboard/static/js/jsocketBridge.swf", 
	// default tcp server port
	"SERVER_PORT": 9999, 
	// name of the 'channel' inside the room
	"APP_NAME": "myapp"
};

// when using flashsocket we need the full path to the SWF
// also the server must server the crosspolicy XML file on port 843
var jsocketBridgeDomain = jsocketConfig.SWF_URI;

// register a new application
jsocket.api.register(jsocketConfig.APP_NAME);

// setup defaults  callbacks
jsocket.api.app[jsocketConfig.APP_NAME].onMessage = function(info) {
	debug('onMessage', info);
	// if we want to execute javascript
	// if (info.value != false && info.value != true && info.value[1]) {
	// eval(info.value[1]).call(this);
	// }
};

jsocket.api.app[ jsocketConfig.APP_NAME ].onForward = function(info) {
	debug('onForward', info);
	// if we want to execute javascript
	//if (info.value != false && info.value != true && info.value[1]) {
	//	eval(info.value[1]);
	// }
}

jsocket.api.app[jsocketConfig.APP_NAME].onChanAuth = function(info) {
	debug('onChanAuth', info);
	// when auth, list users in the channel
	// jsocket.api.list(jsocketConfig.APP_NAME, jsocketConfig.ROOM);
};

jsocket.api.app[jsocketConfig.APP_NAME].onJoin = function(info) {
	debug('onJoin', info);
	jsocket.api.list(jsocketConfig.APP_NAME, jsocketConfig.ROOM);
};

jsocket.api.app[jsocketConfig.APP_NAME].onList = function(info) {
	debug('onList', info);
};

jsocket.api.app[jsocketConfig.APP_NAME].onStatus = function(info) {
	debug( 'onStatus', info );
};


jsocket.api.app[jsocketConfig.APP_NAME].onDisconnected = function(info) {
	debug('onDisconnected', info);
};

// configure the connections
jsocket.api.configure({
	tcp: {
		host: jsocketConfig.SERVER,
		port: jsocketConfig.SERVER_PORT
	},
	http: {
		url: jsocketConfig.URL_FAILOVER
	},
	websocket: {
		host: jsocketConfig.SERVER,
		port: jsocketConfig.SERVER_WEBSOCKET_PORT
	},
	vhost: jsocketConfig.VHOST
});