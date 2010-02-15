/**
 * Includes swf for flash socket bridge
 */
var jsocketFlashHtml = '<embed height="300" width="1000" flashvars="scope=jsocketCore" allowscriptaccess="always" quality="low" bgcolor="#ffffff" name="socketBridge" id="socketBridge" style="" src="' + jsocketDomain + 'ext/jsocketBridge.swf" type="application/x-shockwave-flash">';
document.getElementById('flashcontent').innerHTML = jsocketFlashHtml;
document.getElementById('flashcontent').style.visibility = 'hidden';
document.getElementById('flashcontent').style.position = 'absolute';
