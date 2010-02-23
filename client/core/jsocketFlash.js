/**
* Includes swf for flash socket bridge
**/
swfobject.embedSWF(jsocketBridgeDomain, "flashcontent", "900", "200", "8.0.0", "expressInstall.swf",
	{scope: 'jsocketCore'}, {menu: false}, {id:'socketBridge', name:'socketBridge', style:'position:absolute;top:-1000px;'});
