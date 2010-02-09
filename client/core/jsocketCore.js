/**
 * Javascript event's interface for flash swf socket bridge
 */
var jsocketCore = {
 api = null;
 host = '';
 port = 0;

 loaded : function()
 {
   this.connectedToServer = false;
   this.socket = document.getElementById("socketBridge");
   return (true);
 },
 
 connect : function(server, port)
 {
   this.socket.connect(server, port);
   return (true);
 },
 
 write : function(msg)
 {
   if (this.connectedToServer == false)
     this.connect(this.host, this.port);
   if (this.connectedToServer)
     this.socket.write(msg);
   else
     {
       if (typeof this.api != 'object')
     	 return (false);
       this.api.onDisconnect('{"from": "disconnect", "value": "True"}');
       return (false);
     }
   return (true);
 },
 
 connected : function()
 {
   if (typeof this.api != 'object')
     return (false);
   this.connectedToServer = true;
   this.api.onConnect('{"from": "connect", "value": "true"}');
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
   this.api.onDisconnect('{"form": "disconnect", "value": "true"}');
   this.connectedToServer = false;
   this.reconnect();
   return (true);
 },
 
 ioError: function(msg)
 {
   if (typeof this.api != 'object')
     return (false);
   this.api.onIOError('{"form": "ioError", "value": "' + msg + '"}');
   if (this.connectedToServer == false)
     this.reconnect();
   return (true);
 },
 
 securityError: function(msg)
 {
   if (typeof this.api != 'object')
     return (false);
   this.api.onSecurityError('{"form": "securityError", "value": "' + msg + '"}');
   if (this.connectedToServer == false)
     this.reconnect();
   return (true);
 },
 
 receive: function(msg)
 {
   if (typeof this.api != 'object')
     return (false);
   this.api.onReceive(msg);
   return (true);
 },
 
 reconnect : function()
 {
   this.connect(this.host, this.port);
   if (this.connectedToServer == false)
   {
     setTimeout("this.reconnect();", 1000);
     return (false);
   }
   else
     return (true);
 }
};