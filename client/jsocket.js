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
  document.write('<div id="' + id + '">&nbsp;</div>');
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
			alert(scripts[i].src);
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
