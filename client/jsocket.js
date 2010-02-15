var jsocketDomain = getJsocketDomain();

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

create('div', 'flashcontent');
create('div', 'jsocketBridgeOutput');
includeScript('lib/json-pack.js');
includeScript('core/jsocketCore.js');
includeScript('core/jsocketApi.js');
includeScript('core/jsocketFlash.js');
