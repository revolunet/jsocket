var jsocketDomain = getJsocketDomain();
if (jsocketBridgeDomain == null) {
	var jsocketBridgeDomain = jsocketDomain + 'ext/jsocketBridge.swf';
}

function includeScript(filename)
{
	var script = document.createElement('script');
	script.type = 'text/javascript';
	script.src = jsocketDomain + filename;
	document.getElementsByTagName("head")[0].appendChild(script);
}

function create(type, id)
{
	var docType = document.createElement(type);
	docType.id = id;
	docType.innerHTML = '&nbsp;';
	document.body.appendChild(docType);
}

function getURLBase(url)
{
	return (url.substr(0, url.lastIndexOf("/")) + '/');
}

function getJsocketDomain()
{
	var scripts = document.getElementsByTagName("script");
	for (var i = 0; scripts[i]; ++i) {
		if (scripts[i].src.match(/jsocket.js/i)) {
			return getURLBase(scripts[i].src);
		}
	}
	return (false);
}

jsocket = {
	api : null,
	protocol : null,
	core : {
		http : null,
		tcp : null,
		websocket : null
	}
};

create('div', 'flashcontent');
create('div', 'jsocketBridgeOutput');
includeScript('lib/json2.js');
includeScript('protocol.js');
includeScript('core/tcp.js');
includeScript('core/http.js');
includeScript('core/websocket.js');
includeScript('api.js');
includeScript('flash.js');
