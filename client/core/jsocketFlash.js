/**
 * Includes swf for flash socket bridge
 */
var jsocketFlashContent = '<object width="400" height="300">' +
'<param name="movie" value="ext/jsocketBridge.swf"></param>' +
'<param name="flashvars" value="scope=jsocketCore"></param>' +
'<param name="allowScriptAccess" value="always"></param>' +
'<embed src="ext/jsocketBridge.swf" type="application/x-shockwave-flash" allowScriptAccess="always" name="socketBridge" flashvars="scope=jsocketCore" id="socketBridge"></embed>' +
'</object>';
document.getElementById('jsocketFlashContent').innerHTML = jsocketFlashContent;
