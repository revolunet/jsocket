/**
* Includes swf for flash socket bridge
**/
swfobject.embedSWF(jsocketBridgeDomain, "flashcontent", "900px", "250px", "9.0.0", "expressInstall.swf",
	{scope: 'jsocketCore'},
	{menu: false, quality: 'high', allowScriptAccess: 'always', movie: jsocketBridgeDomain},
	{id:'socketBridge', name:'socketBridge', style:'position:absolute;visibility:hidden;top:500px;'});
