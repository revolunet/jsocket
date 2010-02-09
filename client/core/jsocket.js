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

create('div', 'jsocketFlashContent');
create('div', 'jsocketBridgeOutput');
include_js('lib/json-pack.js');
include_js('core/jsocketCore.js');
include_js('core/jsocketFlash.js');
include_js('core/jsocketAPI.js');
