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
   if (this.initialized == true && this.connectedToServer == false)
   	 this.socket.connect(server, port);
   else
     setTimeout("jsocketCore.reconnect();", 500);
 },

 send : function(msg)
 {
   return (this.write(msg));
 },

 addslashes : function(str)
 {
   str = str.replace(/\\/g, '\\\\');
   str = str.replace(/\'/g, '\\\'');
   str = str.replace(/\"/g, '\\"');
   str = str.replace(/\0/g, '\\0');
   return (str);
 },
 
 stripslashes : function (str)
 {
   str = str.replace(/\\'/g, '\'');
   str = str.replace(/\\"/g, '"');
   str = str.replace(/\\0/g, '\0');
   str = str.replace(/\\\\/g, '\\');
   return (str);
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
       setTimeout("jsocketCore.send('" + msg + "');", 500);
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
   /*if (this.connectedToServer == false)
     setTimeout("jsocketCore.reconnect();", 1000);*/
 }
};