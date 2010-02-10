var jsocketDomain = '';

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

create('div', 'flashcontent');
create('div', 'jsocketBridgeOutput');
includeScript('lib/json-pack.js');
includeScript('core/jsocketCore.js');
includeScript('core/jsocketApi.js');
includeScript('core/jsocketFlash.js');
