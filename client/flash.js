/**
* Includes swf for flash socket bridge
**/
function createSwf() {
	if (typeof swfobject != 'undefined' && typeof jsocket.core.tcp != 'undefined') {
		swfobject.embedSWF(jsocketBridgeDomain, "flashcontent", "900", "200", "8.0.0", "expressInstall.swf",
						   {scope: 'jsocket.core.tcp'}, {menu: false},
						   {id:'socketBridge', name:'socketBridge', style:'position:absolute;top:-1000px;'});
	} else {
		setTimeout('createSwf()', 200);
	}
}

createSwf();
