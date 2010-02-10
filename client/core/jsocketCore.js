/**
 * Javascript event's interface for flash swf socket bridge
 */
var jsocketCore = {
 api : null,
 initialized : false,
 connectedToServer : false,

 loaded : function()
 {
   this.initialized = true;
   this.connectedToServer = false;
   this.socket = document.getElementById("socketBridge");
   this.output = document.getElementById("jsocketBridgeOutput");
   return (true);
 },
 
 connect : function(server, port)
 {
   if (this.initialized == true)
   {
   	 this.socket.connect(server, port);
     return (true);
   }
   return (false);
 },

 send : function(msg)
 {
   return (this.write(msg));
 },

 write : function(msg)
 {
   if (this.connectedToServer == false)
     this.reconnect();
   if (this.connectedToServer)
     this.socket.write(msg);
   else
     {
       if (typeof this.api != 'object')
     	 return (false);
       //this.api.onDisconnect('{"from": "disconnect", "value": "True"}');
       return (false);
     }
   return (true);
 },
 
 connected : function()
 {
   if (typeof this.api != 'object')
     return (false);
   this.connectedToServer = true;
   //this.api.onConnect('{"from": "connect", "value": "true"}');
   return (true);
 },
 
 close : function()
 {
   this.socket.close();
   return (true);
 },
 
 disconnected : function()
 {
   if (typeof this.api != 'object')
     return (false);
   //this.api.onDisconnect('{"from": "disconnect", "value": "true"}');
   this.connectedToServer = false;
   this.reconnect();
   return (true);
 },
 
 ioError: function(msg)
 {
   if (typeof this.api != 'object')
     return (false);
   this.api.onError('{"from": "ioError", "value": "' + msg + '"}');
   if (this.connectedToServer == false)
     this.reconnect();
   return (true);
 },
 
 securityError: function(msg)
 {
   if (typeof this.api != 'object')
     return (false);
   this.api.onError('{"from": "securityError", "value": "' + msg + '"}');
   if (this.connectedToServer == false)
     this.reconnect();
   return (true);
 },
 
 receive: function(msg)
 {
   if (typeof this.api != 'object')
     return (false);
   alert(msg);
   this.api.onReceive(msg);
   return (true);
 },
 
 reconnect : function()
 {
   this.connect(this.api.host, this.api.port);
   if (this.connectedToServer == false)
   {
     setTimeout("jsocketCore.reconnect();", 1000);
     return (false);
   }
   else
     return (true);
 }
};