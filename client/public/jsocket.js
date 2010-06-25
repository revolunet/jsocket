var jsocketDomain = getJsocketDomain();
if (jsocketBridgeDomain == null) {
	var jsocketBridgeDomain = jsocketDomain + 'ext/jsocketBridge.swf';
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
	},
	version: '0.2.6'
};

create('div', 'flashcontent');
create('div', 'jsocketBridgeOutput');

/*
    http://www.JSON.org/json2.js
    2010-03-20

    Public Domain.

    NO WARRANTY EXPRESSED OR IMPLIED. USE AT YOUR OWN RISK.

    See http://www.JSON.org/js.html


    This code should be minified before deployment.
    See http://javascript.crockford.com/jsmin.html

    USE YOUR OWN COPY. IT IS EXTREMELY UNWISE TO LOAD CODE FROM SERVERS YOU DO
    NOT CONTROL.


    This file creates a global JSON object containing two methods: stringify
    and parse.

        JSON.stringify(value, replacer, space)
            value       any JavaScript value, usually an object or array.

            replacer    an optional parameter that determines how object
                        values are stringified for objects. It can be a
                        function or an array of strings.

            space       an optional parameter that specifies the indentation
                        of nested structures. If it is omitted, the text will
                        be packed without extra whitespace. If it is a number,
                        it will specify the number of spaces to indent at each
                        level. If it is a string (such as '\t' or '&nbsp;'),
                        it contains the characters used to indent at each level.

            This method produces a JSON text from a JavaScript value.

            When an object value is found, if the object contains a toJSON
            method, its toJSON method will be called and the result will be
            stringified. A toJSON method does not serialize: it returns the
            value represented by the name/value pair that should be serialized,
            or undefined if nothing should be serialized. The toJSON method
            will be passed the key associated with the value, and this will be
            bound to the value

            For example, this would serialize Dates as ISO strings.

                Date.prototype.toJSON = function (key) {
                    function f(n) {
                        // Format integers to have at least two digits.
                        return n < 10 ? '0' + n : n;
                    }

                    return this.getUTCFullYear()   + '-' +
                         f(this.getUTCMonth() + 1) + '-' +
                         f(this.getUTCDate())      + 'T' +
                         f(this.getUTCHours())     + ':' +
                         f(this.getUTCMinutes())   + ':' +
                         f(this.getUTCSeconds())   + 'Z';
                };

            You can provide an optional replacer method. It will be passed the
            key and value of each member, with this bound to the containing
            object. The value that is returned from your method will be
            serialized. If your method returns undefined, then the member will
            be excluded from the serialization.

            If the replacer parameter is an array of strings, then it will be
            used to select the members to be serialized. It filters the results
            such that only members with keys listed in the replacer array are
            stringified.

            Values that do not have JSON representations, such as undefined or
            functions, will not be serialized. Such values in objects will be
            dropped; in arrays they will be replaced with null. You can use
            a replacer function to replace those with JSON values.
            JSON.stringify(undefined) returns undefined.

            The optional space parameter produces a stringification of the
            value that is filled with line breaks and indentation to make it
            easier to read.

            If the space parameter is a non-empty string, then that string will
            be used for indentation. If the space parameter is a number, then
            the indentation will be that many spaces.

            Example:

            text = JSON.stringify(['e', {pluribus: 'unum'}]);
            // text is '["e",{"pluribus":"unum"}]'


            text = JSON.stringify(['e', {pluribus: 'unum'}], null, '\t');
            // text is '[\n\t"e",\n\t{\n\t\t"pluribus": "unum"\n\t}\n]'

            text = JSON.stringify([new Date()], function (key, value) {
                return this[key] instanceof Date ?
                    'Date(' + this[key] + ')' : value;
            });
            // text is '["Date(---current time---)"]'


        JSON.parse(text, reviver)
            This method parses a JSON text to produce an object or array.
            It can throw a SyntaxError exception.

            The optional reviver parameter is a function that can filter and
            transform the results. It receives each of the keys and values,
            and its return value is used instead of the original value.
            If it returns what it received, then the structure is not modified.
            If it returns undefined then the member is deleted.

            Example:

            // Parse the text. Values that look like ISO date strings will
            // be converted to Date objects.

            myData = JSON.parse(text, function (key, value) {
                var a;
                if (typeof value === 'string') {
                    a =
/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2}(?:\.\d*)?)Z$/.exec(value);
                    if (a) {
                        return new Date(Date.UTC(+a[1], +a[2] - 1, +a[3], +a[4],
                            +a[5], +a[6]));
                    }
                }
                return value;
            });

            myData = JSON.parse('["Date(09/09/2001)"]', function (key, value) {
                var d;
                if (typeof value === 'string' &&
                        value.slice(0, 5) === 'Date(' &&
                        value.slice(-1) === ')') {
                    d = new Date(value.slice(5, -1));
                    if (d) {
                        return d;
                    }
                }
                return value;
            });


    This is a reference implementation. You are free to copy, modify, or
    redistribute.
*/

/*jslint evil: true, strict: false */

/*members "", "\b", "\t", "\n", "\f", "\r", "\"", JSON, "\\", apply,
    call, charCodeAt, getUTCDate, getUTCFullYear, getUTCHours,
    getUTCMinutes, getUTCMonth, getUTCSeconds, hasOwnProperty, join,
    lastIndex, length, parse, prototype, push, replace, slice, stringify,
    test, toJSON, toString, valueOf
*/


// Create a JSON object only if one does not already exist. We create the
// methods in a closure to avoid creating global variables.

if (!this.JSON) {
    this.JSON = {};
}

(function () {

    function f(n) {
        // Format integers to have at least two digits.
        return n < 10 ? '0' + n : n;
    }

    if (typeof Date.prototype.toJSON !== 'function') {

        Date.prototype.toJSON = function (key) {

            return isFinite(this.valueOf()) ?
                   this.getUTCFullYear()   + '-' +
                 f(this.getUTCMonth() + 1) + '-' +
                 f(this.getUTCDate())      + 'T' +
                 f(this.getUTCHours())     + ':' +
                 f(this.getUTCMinutes())   + ':' +
                 f(this.getUTCSeconds())   + 'Z' : null;
        };

        String.prototype.toJSON =
        Number.prototype.toJSON =
        Boolean.prototype.toJSON = function (key) {
            return this.valueOf();
        };
    }

    var cx = /[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,
        escapable = /[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,
        gap,
        indent,
        meta = {    // table of character substitutions
            '\b': '\\b',
            '\t': '\\t',
            '\n': '\\n',
            '\f': '\\f',
            '\r': '\\r',
            '"' : '\\"',
            '\\': '\\\\'
        },
        rep;


    function quote(string) {

// If the string contains no control characters, no quote characters, and no
// backslash characters, then we can safely slap some quotes around it.
// Otherwise we must also replace the offending characters with safe escape
// sequences.

        escapable.lastIndex = 0;
        return escapable.test(string) ?
            '"' + string.replace(escapable, function (a) {
                var c = meta[a];
                return typeof c === 'string' ? c :
                    '\\u' + ('0000' + a.charCodeAt(0).toString(16)).slice(-4);
            }) + '"' :
            '"' + string + '"';
    }


    function str(key, holder) {

// Produce a string from holder[key].

        var i,          // The loop counter.
            k,          // The member key.
            v,          // The member value.
            length,
            mind = gap,
            partial,
            value = holder[key];

// If the value has a toJSON method, call it to obtain a replacement value.

        if (value && typeof value === 'object' &&
                typeof value.toJSON === 'function') {
            value = value.toJSON(key);
        }

// If we were called with a replacer function, then call the replacer to
// obtain a replacement value.

        if (typeof rep === 'function') {
            value = rep.call(holder, key, value);
        }

// What happens next depends on the value's type.

        switch (typeof value) {
        case 'string':
            return quote(value);

        case 'number':

// JSON numbers must be finite. Encode non-finite numbers as null.

            return isFinite(value) ? String(value) : 'null';

        case 'boolean':
        case 'null':

// If the value is a boolean or null, convert it to a string. Note:
// typeof null does not produce 'null'. The case is included here in
// the remote chance that this gets fixed someday.

            return String(value);

// If the type is 'object', we might be dealing with an object or an array or
// null.

        case 'object':

// Due to a specification blunder in ECMAScript, typeof null is 'object',
// so watch out for that case.

            if (!value) {
                return 'null';
            }

// Make an array to hold the partial results of stringifying this object value.

            gap += indent;
            partial = [];

// Is the value an array?

            if (Object.prototype.toString.apply(value) === '[object Array]') {

// The value is an array. Stringify every element. Use null as a placeholder
// for non-JSON values.

                length = value.length;
                for (i = 0; i < length; i += 1) {
                    partial[i] = str(i, value) || 'null';
                }

// Join all of the elements together, separated with commas, and wrap them in
// brackets.

                v = partial.length === 0 ? '[]' :
                    gap ? '[\n' + gap +
                            partial.join(',\n' + gap) + '\n' +
                                mind + ']' :
                          '[' + partial.join(',') + ']';
                gap = mind;
                return v;
            }

// If the replacer is an array, use it to select the members to be stringified.

            if (rep && typeof rep === 'object') {
                length = rep.length;
                for (i = 0; i < length; i += 1) {
                    k = rep[i];
                    if (typeof k === 'string') {
                        v = str(k, value);
                        if (v) {
                            partial.push(quote(k) + (gap ? ': ' : ':') + v);
                        }
                    }
                }
            } else {

// Otherwise, iterate through all of the keys in the object.

                for (k in value) {
                    if (Object.hasOwnProperty.call(value, k)) {
                        v = str(k, value);
                        if (v) {
                            partial.push(quote(k) + (gap ? ': ' : ':') + v);
                        }
                    }
                }
            }

// Join all of the member texts together, separated with commas,
// and wrap them in braces.

            v = partial.length === 0 ? '{}' :
                gap ? '{\n' + gap + partial.join(',\n' + gap) + '\n' +
                        mind + '}' : '{' + partial.join(',') + '}';
            gap = mind;
            return v;
        }
    }

// If the JSON object does not yet have a stringify method, give it one.

    if (typeof JSON.stringify !== 'function') {
        JSON.stringify = function (value, replacer, space) {

// The stringify method takes a value and an optional replacer, and an optional
// space parameter, and returns a JSON text. The replacer can be a function
// that can replace values, or an array of strings that will select the keys.
// A default replacer method can be provided. Use of the space parameter can
// produce text that is more easily readable.

            var i;
            gap = '';
            indent = '';

// If the space parameter is a number, make an indent string containing that
// many spaces.

            if (typeof space === 'number') {
                for (i = 0; i < space; i += 1) {
                    indent += ' ';
                }

// If the space parameter is a string, it will be used as the indent string.

            } else if (typeof space === 'string') {
                indent = space;
            }

// If there is a replacer, it must be a function or an array.
// Otherwise, throw an error.

            rep = replacer;
            if (replacer && typeof replacer !== 'function' &&
                    (typeof replacer !== 'object' ||
                     typeof replacer.length !== 'number')) {
                throw new Error('JSON.stringify');
            }

// Make a fake root object containing our value under the key of ''.
// Return the result of stringifying the value.

            return str('', {'': value});
        };
    }


// If the JSON object does not yet have a parse method, give it one.

    if (typeof JSON.parse !== 'function') {
        JSON.parse = function (text, reviver) {

// The parse method takes a text and an optional reviver function, and returns
// a JavaScript value if the text is a valid JSON text.

            var j;

            function walk(holder, key) {

// The walk method is used to recursively walk the resulting structure so
// that modifications can be made.

                var k, v, value = holder[key];
                if (value && typeof value === 'object') {
                    for (k in value) {
                        if (Object.hasOwnProperty.call(value, k)) {
                            v = walk(value, k);
                            if (v !== undefined) {
                                value[k] = v;
                            } else {
                                delete value[k];
                            }
                        }
                    }
                }
                return reviver.call(holder, key, value);
            }


// Parsing happens in four stages. In the first stage, we replace certain
// Unicode characters with escape sequences. JavaScript handles many characters
// incorrectly, either silently deleting them, or treating them as line endings.

            text = String(text);
            cx.lastIndex = 0;
            if (cx.test(text)) {
                text = text.replace(cx, function (a) {
                    return '\\u' +
                        ('0000' + a.charCodeAt(0).toString(16)).slice(-4);
                });
            }

// In the second stage, we run the text against regular expressions that look
// for non-JSON patterns. We are especially concerned with '()' and 'new'
// because they can cause invocation, and '=' because it can cause mutation.
// But just to be safe, we want to reject all unexpected forms.

// We split the second stage into 4 regexp operations in order to work around
// crippling inefficiencies in IE's and Safari's regexp engines. First we
// replace the JSON backslash pairs with '@' (a non-JSON character). Second, we
// replace all simple value tokens with ']' characters. Third, we delete all
// open brackets that follow a colon or comma or that begin the text. Finally,
// we look to see that the remaining characters are only whitespace or ']' or
// ',' or ':' or '{' or '}'. If that is so, then the text is safe for eval.

            if (/^[\],:{}\s]*$/.
test(text.replace(/\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g, '@').
replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g, ']').
replace(/(?:^|:|,)(?:\s*\[)+/g, ''))) {

// In the third stage we use the eval function to compile the text into a
// JavaScript structure. The '{' operator is subject to a syntactic ambiguity
// in JavaScript: it can begin a block or an object literal. We wrap the text
// in parens to eliminate the ambiguity.

                j = eval('(' + text + ')');

// In the optional fourth stage, we recursively walk the new structure, passing
// each name/value pair to a reviver function for possible transformation.

                return typeof reviver === 'function' ?
                    walk({'': j}, '') : j;
            }

// If the text is not JSON parseable, then a SyntaxError is thrown.

            throw new SyntaxError('JSON.parse');
        };
    }
}());

/**
 * @class jsocket.protocol
 * <p><b><u>jsocket Protocol</u></b></p>
 * <p>Valide et forge le JSON des commandes a partir d'un objet.</p>
 * @author Revolunet
 * @version 0.2.6
 * @singleton
 */
jsocket.protocol = {
	/**
	 * Forge une commande JSON a partir d'un objet javascript
	 * @param {Object} obj Objet javascript
	 * @return {String} Commande JSON
	 */
	forge : function(obj) {
		for (var i in obj) {
			obj[i] = jsocket.api.core.addslashes(obj[i]);
		}
		return (JSON.stringify(obj));
	}
};

/**
 * @class jsocket.core.tcp
 * Javascript event's interface for flash swf socket bridge
 * @author Revolunet
 * @version 0.2.6
 * @singleton
 */
jsocket.core.tcp = {
	/**
	 * Pointeur vers l'API
	 * @private
	 * @type {@link jsocket.api}
	 */
	api: null,

	/**
	 * True si le core a ete initialize sinon False
	 * @private
	 * @type Boolean
	 */
	initialized: false,

	/**
	 * True si le core est connecte au server sinon False
	 * @private
	 * @type Boolean
	 */
	connectedToServer: false,

	/**
	 * True si ce core est utilise par l'API sinon False
	 * @private
	 * @type Boolean
	 */
	isWorking: false,

	/**
	 * Determine si la deconnection a ete forcer ou non
	 * @private
	 * @type Boolean
	 */
	manuallyDisconnected: false,

	/**
	 * @event loaded
	 * Callback appele par flash lorsque le swf est charge
	 * @return {Boolean} True si l'application a ete chargee
	 */
	loaded: function() {
		jsocket.core.tcp.initialized = true;
		jsocket.core.tcp.connectedToServer = false;
		jsocket.core.tcp.socket = document.getElementById("socketBridge");
		jsocket.core.tcp.output = document.getElementById("jsocketBridgeOutput");
		return (true);
	},

	/**
	 * Initialise une connection via une socket sur le server:port
	 */
	connect: function() {
		if (jsocket.core.tcp.initialized == true && jsocket.core.tcp.connectedToServer == false) {
			jsocket.core.tcp.socket.connect(jsocket.api.settings.tcp.host, jsocket.api.settings.tcp.port);
		}
		else if (jsocket.core.tcp.connectedToServer == false) {
			jsocket.core.tcp.setTimeout("jsocket.core.tcp.connect();", 500);
		}
	},

	/**
	 * Lance un setTimeout sur cmd avec comme temps d'attente delay a
	 * condition que ce core est utilise par l'API
	 * @param {String} cmd La commande a lancer
	 * @param {Int} delay Le temps d'attente
	 */
	setTimeout: function(cmd, delay) {
		if (jsocket.core.tcp.isWorking == true) {
			setTimeout(cmd, delay);
		}
	},

	/**
	 * Addslashes les caracteres ' " \\ \0
	 * @param {String} str Le texte a addslasher
	 * @return {String} La chaine avec les caracteres echapes
	 */
	addslashes: function(str) {
		if (typeof(str) == 'string') {
			str = encodeURIComponent(str);
			str = str.replace(/\'/g, "%27");
		}
		else if (typeof(str) == 'object') {
			for (var i in str) {
				str[i] = jsocket.core.tcp.addslashes(str[i]);
			}
		}
		return (str);
	},

	/**
	 * Supprime tous les slashes des caracteres ' " \\ \0
	 * @param {String} str Le texte a stripslasher
	 * @return {String} La chaine avec les caracteres non echapes
	 */
	stripslashes: function (str) {
		if (typeof(str) == 'string') {
			str = str.replace(/\%27/g, "'");
			str = decodeURIComponent(str);
		}
		else if (typeof(str) == 'object') {
			for (var i in str) {
				str[i] = jsocket.core.tcp.stripslashes(str[i]);
			}
		}
		return (str);
	},

	/**
	 * Envoie le message au serveur.
	 * Tentative de reconnection a ce dernier le cas echeant.
	 * @param {String} msg Le texte a envoyer au serveur
	 * @return {Boolean} True si le message a ete envoye sinon False
	 */
	write: function(msg) {
		if (jsocket.core.tcp.connectedToServer == false) {
			jsocket.core.tcp.connect();
		}
		if (jsocket.core.tcp.connectedToServer) {
			jsocket.core.tcp.socket.write(msg + "\n");
		} else {
			if (typeof jsocket.core.tcp.api != 'object') {
				return (false);
			}
			jsocket.core.tcp.setTimeout("jsocket.core.tcp.send('" + msg + "');", 500);
			return (false);
		}
		return (true);
	},

	/**
	 * Alias de {@link #write write}
	 * @param {String} msg Le message a envoye au serveur
	 * @return {Boolean} True si le message a ete envoye sinon False
	 */
	send: function(msg) {
		return (jsocket.core.tcp.write(msg));
	},

	/**
	 * @event connected
	 * Callback appele par flash lorsque la socket est connectee au serveur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	connected: function() {
		if (typeof jsocket.core.tcp.api != 'object') {
			return (false);
		}
		jsocket.core.tcp.connectedToServer = true;
		jsocket.core.tcp.send('{"cmd": "connected", "args": "null", "app": ""}');
		jsocket.core.tcp.api.onReceive('{"from": "connect", "value": true}');
		return (true);
	},

	/**
	 * Ferme la connection au serveur
	 * @return {Boolean} True si la connection a ete fermee sinon False
	 */
	close: function() {
		jsocket.core.tcp.socket.close();
		jsocket.core.tcp.manuallyDisconnected = true;
		return (true);
	},

	/**
	 * @event disconnected
	 * Callback appele par flash lorsqu'une deconnection a ete effectuee
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	disconnected: function() {
		if (typeof jsocket.core.tcp.api != 'object') {
			return (false);
		}
		jsocket.core.tcp.api.uid = '';
		jsocket.core.tcp.api.parser('{"from": "disconnect", "value": true}');
		jsocket.core.tcp.connectedToServer = false;
		if (jsocket.core.tcp.manuallyDisconnected == true) {
			jsocket.core.tcp.manuallyDisconnected = false;
		} else {
			jsocket.core.tcp.connect();
		}
		return (true);
	},

	/**
	 * @event ioError
	 * Callback appele par flash lorsqu'une Input/Output erreur survient
	 * @param {String} msg Le message ainsi que le code d'erreur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	ioError: function(msg) {
		if (typeof jsocket.core.tcp.api != 'object') {
			return (false);
		}
		jsocket.core.tcp.api.parser('{"from": "error", "value": "' + msg + '"}');
		if (jsocket.core.tcp.connectedToServer == false) {
			jsocket.core.tcp.api.parser('{"from": "TCPError", "value": "Input/Output error"}');
		}
		return (true);
	},

	/**
	 * @event securityError
	 * Callback appele par flash lorsqu'une erreur de securite survient
	 * @param {String} msg Le message ainsi que le code d'erreur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	securityError: function(msg) {
		if (typeof jsocket.core.tcp.api != 'object') {
			return (false);
		}
		jsocket.core.tcp.api.parser('{"from": "error", "value": "' + msg + '"}');
		if (jsocket.core.tcp.connectedToServer == false) {
			jsocket.core.tcp.api.parser('{"from": "TCPError", "value": "Security error"}');
		}
		return (true);
	},

	/**
	 * @event receive
	 * Callback appele par flash lors de la reception d'un message via la socket
	 * @param {String} msg Le message envoye par le serveur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	receive: function(msg) {
		if (typeof jsocket.core.tcp.api != 'object') {
			return (false);
		}
		var tab = msg.split("\n");
		for (var i = 0; i < tab.length; ++i) {
			jsocket.core.tcp.api.onReceive(tab[i]);
		}
		return (true);
	}
};

/**
 * @class jsocket.core.http
 * Javascript event's interface fail over HTTP
 * @author Revolunet
 * @version 0.2.6
 * @singleton
 */
jsocket.core.http = {
	/**
	 * <p><b><u>Settings:</u></b></p>
	 * <div class="mdetail-params"><ul>
	 * <li><b><tt>refreshTimer: Temps de rafraichissement entre chaque requetes</tt></b></li>
	 * </ul></div></p>
	 * @public
	 * @type Object
	 */
	settings: {
		refreshTimer: 2000
	},

	/**
	 * <p><b><u>Response:</u></b></p>
	 * <div class="mdetail-params"><ul>
	 * <li><b><tt>waiting: true si une requete est en attente de reponse sinon false</tt></b></li>
	 * <li><b><tt>lastTime: timestamp de la derniere reponse obtenue</tt></b></li>
	 * <li><b><tt>timeout: temps en seconde avant de relancer une requete si il n'y a pas
	 * eu de reponse positive entre temps</tt></b></li>
	 * </ul></div></p>
	 * @public
	 * @type Object
	 */
	response: {
		waiting: false,
		lastTime: 0,
		timeout: 5
	},

	/**
	 * Pointeur vers l'API
	 * @private
	 * @type {@link jsocket.api}
	 */
	api: null,

	/**
	 * True si le core a ete initialize sinon False
	 * @private
	 * @type Boolean
	 */
	initialized: false,

	/**
	 * True si le core est connecte au server sinon False
	 * @private
	 * @type Boolean
	 */
	connectedToServer: false,

	/**
	 * Liste des commandes en attente
	 * @private
	 * @type Array
	 */
	commands: [ ],

	/**
	 * Objet comprenant la connection AJAX
	 * @private
	 * @type Object
	 */
	socket: null,

	/**
	 * True si ce core est utilise par l'API sinon False
	 * @private
	 * @type Boolean
	 */
	isWorking: false,

	/**
	 * Initialisation du core HTTP
	 * @return {Boolean} True si l'application a ete chargee
	 */
	loaded: function()	{
		jsocket.core.http.initialized = true;
		return (true);
	},

	/**
	 * Permet d'effectuer une requete HTTP POST sur le serveur (host, port)
	 * @param {String} parameters La commande JSON a envoyee
	 * @return {Boolean} True si la commande a ete envoyee sinon False
	 */
	_post: function(parameters) {
		parameters = encodeURI('json=' + parameters);
		if (window.XMLHttpRequest) {
			jsocket.core.http.socket = new XMLHttpRequest();
		} else {
			jsocket.core.http.socket = new ActiveXObject("Microsoft.XMLHTTP");
		}
		if (!jsocket.core.http.socket) {
			alert('Cannot create XMLHTTP instance');
			return (false);
		}
		jsocket.core.http.socket.onreadystatechange = jsocket.core.http.receive;
		jsocket.core.http.socket.open('POST', jsocket.api.settings.http.url, true);
		jsocket.core.http.socket.send(parameters);
		jsocket.core.http.response.waiting = true;
		return (true);
	},

	/**
	 * Initialise une connection via une socket sur le server:port
	 */
	connect: function() {
		jsocket.core.http.loaded();
		jsocket.core.http.send('{"cmd": "connected", "args": "null", "app": ""}');
		jsocket.core.http.pool();
	},

	/**
	 * Addslashes les caracteres ' " \\ \0
	 * @param {String} str Le texte a addslasher
	 * @return {String} La chaine avec les caracteres echapes
	 */
	addslashes: function(str) {
		if (typeof(str) == 'string') {
			str = encodeURIComponent(str);
			str = str.replace(/\'/g, "%27");
		}
		else if (typeof(str) == 'object') {
			for (var i in str) {
				str[i] = jsocket.core.http.addslashes(str[i]);
			}
		}
		return (str);
	},

	/**
	 * Supprime tous les slashes des caracteres ' " \\ \0
	 * @param {String} str Le texte a stripslasher
     * @return {String} La chaine avec les caracteres non echapes
	 */
	stripslashes: function (str) {
		if (typeof(str) == 'string') {
			str = str.replace(/\%27/g, "'");
			str = decodeURIComponent(str);
		}
		else if (typeof(str) == 'object') {
			for (var i in str) {
				str[i] = jsocket.core.http.stripslashes(str[i]);
			}
		}
		return (str);
	},

	/**
	 * Pool le serveur HTTP en envoyant les requetes des n dernieres
	 * secondes du client et pour obtenir les reponses des commandes
	 * actuelles/precedentes
	 * @return {Boolean} False si l'API n'est pas definie
	 */
	pool: function() {
		if (typeof jsocket.core.http.api != 'object') {
			return (false);
		}
		jsocket.core.http.write();
		setTimeout("jsocket.core.http.pool();", jsocket.core.http.settings.refreshTimer);
	},

	/**
	 * Ferme la connection au serveur
	 * @return {Boolean} True si la connection a ete fermee sinon False
	 */
	close: function() {
		jsocket.core.http.connectedToServer = false;
		return (true);
	},

	/**
	 * Verifie si une commande peut etre envoye au serveur
	 * @return {Boolean} True si la commande peut etre envoyee sinon False
	 */
	checkResponse: function() {
		var now = Math.floor(new Date().getTime() / 1000);
		if (jsocket.core.http.response.waiting == false) {
			return (true);
		} else if ((now - jsocket.core.http.response.lastTime) > jsocket.core.http.response.timeout) {
			jsocket.core.http.response.lastTime = now;
			return (true);
		}
		return (false);
	},

	/**
	 * Envoie les commandes stockees prealablement au serveur.
	 * @return {Boolean} True si les commandes ont ete envoyees sinon False
	 */
	write: function() {
		if (typeof jsocket.core.http.api != 'object' ||
			jsocket.core.http.checkResponse() == false) {
			return (false);
		}
		msg = '';
		if (jsocket.core.http.commands.length > 0) {
			msg = jsocket.core.http.commands.join("\n");
			jsocket.core.http.commands = [ ];
			jsocket.core.http._post(msg + "\n");
		} else {
			jsocket.core.http._post('{"cmd": "refresh", "args": "null", "app": "", "uid": "' +
			  jsocket.core.http.api.uid + '"}\n');
		}
		return (true);
	},

	/**
	 * Alias de {@link #write write}
	 * @param {String} msg Le message a envoye au serveur
	 * @return {Boolean} True si le message a ete envoye sinon False
	 */
	send: function(msg) {
		if (msg.length > 0) {
			return (jsocket.core.http.commands.push(msg));
		}
		return (false);
	},

	/**
	 * @event connected
	 * Callback appele par flash lorsque la socket est connectee au serveur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	connected: function() {
		if (typeof jsocket.core.http.api != 'object') {
			return (false);
		}
		jsocket.core.http.connectedToServer = true;
		jsocket.core.http.api.onReceive('{"from": "connect", "value": true}');
		return (true);
	},

	/**
	 * @event disconnected
	 * Callback appele par flash lorsqu'une deconnection a ete effectuee
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	disconnected: function() {
		if (typeof jsocket.core.http.api != 'object') {
			return (false);
		}
		jsocket.core.http.api.parser('{"from": "disconnect", "value": true}');
		jsocket.core.http.connectedToServer = false;
		jsocket.core.http.connect();
		return (true);
	},

	/**
	 * @event receive
	 * Callback appele par socket lors de la reception d'un message
	 * @return {Boolean} True si la commande a ete envoyee a l'API sinon False
	 */
	receive: function()	{
		if (typeof jsocket.core.http.api != 'object') {
			return (false);
		}
		if (jsocket.core.http.socket.readyState == 4) {
			if (jsocket.core.http.socket.status == 200) {
				if (jsocket.core.http.connectedToServer == false) {
					jsocket.core.http.connected();
				}
				jsocket.core.http.response.waiting = false;
				jsocket.core.http.response.lastTime = Math.floor(new Date().getTime() / 1000);
				msg = jsocket.core.http.socket.responseText;
				if (msg != '') {
					res = msg.split("\n");
					for (var i = 0; res[i]; ++i) {
						jsocket.core.http.api.onReceive(res[i]);
					}
				}
			} else {
				jsocket.core.http.api.parser('{"from": "error", "value": "HTTP request error: ' +
					jsocket.core.http.socket.status + '"}');
			}
		}
		return (true);
	}
};

/**
 * @class jsocket.core.websocket
 * Javascript event's interface for websocket HTML 5
 * @author Revolunet
 * @version 0.2.6
 * @singleton
 */
jsocket.core.websocket = {
	/**
	 * Pointeur vers l'API
	 * @private
	 * @type {@link jsocket.api}
	 */
	api: null,

	/**
	 * True si le core a ete initialize sinon False
	 * @private
	 * @type Boolean
	 */
	initialized: false,

	/**
	 * True si le core est connecte au server sinon False
	 * @private
	 * @type Boolean
	 */
	connectedToServer: false,

	/**
	 * True si ce core est utilise par l'API sinon False
	 * @private
	 * @type Boolean
	 */
	isWorking: false,

	/**
	 * Socket
	 * @private
	 * @type WebSocket
	 */
	socket: null,

	/**
	 * @event loaded
	 * Initialisation du code WebSocket
	 * @return {Boolean} True si l'application a ete chargee
	 */
	loaded: function() {
		if ('WebSocket' in window) {
			jsocket.core.websocket.initialized = true;
			jsocket.core.websocket.connectedToServer = false;
			return (true);
		}
		jsocket.core.websocket.initialized = false;
		jsocket.core.websocket.connectedToServer = false;
		return (false);
	},

	/**
	 * Initialise une connection via une socket sur le server:port
	 */
	connect: function() {
		jsocket.core.websocket.loaded();
		if (jsocket.core.websocket.initialized == true && jsocket.core.websocket.connectedToServer == false) {
			jsocket.core.websocket.socket = new WebSocket('ws://' + jsocket.api.settings.websocket.host + ':' + jsocket.api.settings.websocket.port + '/jsocket');
			jsocket.core.websocket.socket.onmessage = jsocket.core.websocket.receive;
			jsocket.core.websocket.socket.onerror = jsocket.core.websocket.error;
			jsocket.core.websocket.socket.onopen = jsocket.core.websocket.connected;
			jsocket.core.websocket.socket.onclose = jsocket.core.websocket.disconnected;
		}
		else if (jsocket.core.websocket.connectedToServer == false) {
			jsocket.core.websocket.setTimeout("jsocket.core.websocket.connect();", 500);
		}
	},

	/**
	 * @event connected
	 * Callback appele par flash lorsque la socket est connectee au serveur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	connected: function() {
		if (typeof jsocket.core.websocket.api != 'object') {
			return (false);
		}
		jsocket.core.websocket.connectedToServer = true;
		jsocket.core.websocket.api.onReceive('{"from": "connect", "value": true}');
		jsocket.core.websocket.socket.send('{"cmd": "connected", "args": "null", "app": ""}');
		return (true);
	},

	/**
	 * @event disconnected
	 * Callback appele par flash lorsqu'une deconnection a ete effectuee
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	disconnected: function() {
		if (typeof jsocket.core.websocket.api != 'object') {
			return (false);
		}
		jsocket.core.websocket.api.uid = '';
		jsocket.core.websocket.api.parser('{"from": "disconnect", "value": true}');
		jsocket.core.websocket.connectedToServer = false;
		if (jsocket.core.websocket.manuallyDisconnected == true) {
			jsocket.core.websocket.manuallyDisconnected = false;
		} else {
			jsocket.core.websocket.connect();
		}
		return (true);
	},

	/**
	 * @event error
	 * Callback appele par WebSocket lorsqu'une erreur survient
	 * @param {String} msg Le message ainsi que le code d'erreur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	error: function(msg) {
		if (typeof jsocket.core.websocket.api != 'object') {
			return (false);
		}
		jsocket.core.websocket.api.parser('{"from": "error", "value": "' + msg + '"}');
		return (true);
	},

	/**
	 * @event receive
	 * Callback appele par WebSocket lors de la reception d'un message
	 * @param {String} msg Le message envoye par le serveur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	receive: function(msg) {
		if (typeof jsocket.core.websocket.api != 'object') {
			return (false);
		}
		msg = msg.data;
		if (msg.data == '{"from": "connect", "value": "true"}') {
			jsocket.core.websocket.send('{"cmd": "connected", "args": "null", "app": ""}');
		}
		var tab = msg.split("\n");
		for (var i = 0; i < tab.length; ++i) {
			jsocket.core.websocket.api.onReceive(tab[i]);
		}
		return (true);
	},

	/**
	 * Lance un setTimeout sur cmd avec comme temps d'attente delay a
	 * condition que ce core est utilise par l'API
	 * @param {String} cmd La commande a lancer
	 * @param {Int} delay Le temps d'attente
	 */
	setTimeout: function(cmd, delay) {
		if (jsocket.core.websocket.isWorking == true) {
			setTimeout(cmd, delay);
		}
	},

	/**
	 * Addslashes les caracteres ' " \\ \0
	 * @param {String} str Le texte a addslasher
	 * @return {String} La chaine avec les caracteres echapes
	 */
	addslashes: function(str) {
		if (typeof(str) == 'string') {
			str = encodeURIComponent(str);
			str = str.replace(/\'/g, "%27");
		}
		else if (typeof(str) == 'object') {
			for (var i in str) {
				str[i] = jsocket.core.websocket.addslashes(str[i]);
			}
		}
		return (str);
	},

	/**
	 * Supprime tous les slashes des caracteres ' " \\ \0
	 * @param {String} str Le texte a stripslasher
	 * @return {String} La chaine avec les caracteres non echapes
	 */
	stripslashes: function (str) {
		if (typeof(str) == 'string') {
			str = str.replace(/\%27/g, "'");
			str = decodeURIComponent(str);
		}
		else if (typeof(str) == 'object') {
			for (var i in str) {
				str[i] = jsocket.core.websocket.stripslashes(str[i]);
			}
		}
		return (str);
	},

	/**
	 * Envoie le message au serveur.
	 * Tentative de reconnection a ce dernier le cas echeant.
	 * @param {String} msg Le texte a envoyer au serveur
	 * @return {Boolean} True si le message a ete envoye sinon False
	 */
	write: function(msg) {
		if (jsocket.core.websocket.connectedToServer == false) {
			jsocket.core.websocket.connect();
		}
		if (jsocket.core.websocket.connectedToServer) {
			jsocket.core.websocket.socket.send(msg + "\n");
		} else {
			if (typeof jsocket.core.websocket.api != 'object') {
				return (false);
			}
			jsocket.core.websocket.setTimeout("jsocket.core.websocket.send('" + msg + "');", 500);
			return (false);
		}
		return (true);
	},

	/**
	 * Alias de {@link #write write}
	 * @param {String} msg Le message a envoye au serveur
	 * @return {Boolean} True si le message a ete envoye sinon False
	 */
	send: function(msg) {
		return (jsocket.core.websocket.write(msg));
	},

	/**
	 * Ferme la connection au serveur
	 * @return {Boolean} True si la connection a ete fermee sinon False
	 */
	close: function() {
		jsocket.core.websocket.socket.close();
		return (true);
	}
};

/**
 * @class jsocket.api
 * <p><b><u>jsocket API</u></b></p>
 * <p>Chaque callback est appele avec en parametres un dictionnaire comprenant les attributs
 * suivants:
 * <div class="mdetail-params"><ul>
 * <li><b><tt>param.value: value JSON field (empty string '' if not exists)</tt></b></li>
 * <li><b><tt>param.app: app JSON field (empty string '' if not exists)</tt></b></li>
 * <li><b><tt>param.channel: channel JSON field (empty string '' if not exists)</tt></b></li>
 * </ul></div></p>
 *
 * <p><b><u>Exemple:</u></b></p>
<pre><code>
jsocket.api.app['myapp'].onJoin(args) {
  args.value = true;
  args.app = 'myapp';
  args.channel = 'myapp_channel';
};
</code></pre>
 * @author Revolunet
 * @version 0.2.6
 * @singleton
 */
jsocket.api = {
	/**
	 * Le core a utiliser par defaut
	 * @private
	 * @type Object
	 */
	core: null,

	/**
	 * A activer pour afficher les commandes JSON en entree/sortie
	 * @private
	 * @type Boolean
	 */
	debug: false,

	/**
	 * Le tableau des applications enregistrees dans l'API
	 * @private
	 * @type Array
	 */
	app: [ ],

	/**
	 * L'uid du client une fois connecte
	 * @public
	 * @type String
	 */
	uid: '',

	/**
	 * La liste des commandes en attente d'envoie
	 * @private
	 * @type Array
	 */
	commands: [ ],

	/**
	 * La liste des cores disponibles.
	 * Si un core ne fonctionne pas, alors
	 * le core suivant est teste.
	 * @private
	 * @type Object
	 */
	cores: {
		tcp: {
			object: jsocket.core.tcp,
			tested: false,
			worked: true
		},
		http: {
			object: jsocket.core.http,
			tested: false,
			worked: true
		},
		websocket: {
			object: jsocket.core.websocket,
			tested: false,
			worked: true
		}
	},

	/**
	 * <p>Parametres de configuration:</p>
	 * <p><div class="mdetail-params"><ul>
	 * <li><b><tt>tcp.host: Host pour le core {@link jsocket.core.tcp}</tt></b></li>
	 * <li><b><tt>tcp.port: Port pour le core {@link jsocket.core.tcp}</tt></b></li>
	 * <li><b><tt>http.url: Url pour le core {@link jsocket.core.http}</tt></b></li>
	 * <li><b><tt>websocket.host: Host pour le core {@link jsocket.core.websocket}</tt></b></li>
	 * <li><b><tt>websocket.port: Port pour le core {@link jsocket.core.websocket}</tt></b></li>
	 * </ul></div></p>
	 * Ce parametre peut etre changer directement comme dans l'exemple ci-dessous
	 * ou via la methode {@link jsocket.api.configure}
	 * <p><b><u>Exemple de configuration:</u></b></p>
<pre><code>
jsocket.api.settings = {
  tcp: {
    host: 'localhost',
	port: 8080
  },
  http: {
    url: 'http://localhost:8081/'
  },
  websocket: {
    host: 'localhost',
    port: 8082
  }
};
</code></pre>
	 */
	settings: {
		tcp: {
			host: 'localhost',
			port: 8080
		},
		http: {
			url: 'http://localhost:8081/'
		},
		websocket: {
			host: 'localhost',
			port: 8082
		}
	},

	/**
	 * <p>Connection au serveur via le jsocket.core</p>
	 * @param {Object} Parametre optionnel de configuration {@link jsocket.api.settings}
	 */
	connect: function(settings) {
		if (typeof settings != undefined && settings != null) {
			jsocket.api.configure(settings);
		}
		if (jsocket.api.core == null) {
			jsocket.api.setCore();
		}
		jsocket.api.core.api = this;
		jsocket.api.core.connect();
	},

	/**
	 * <p>Permet de changer la configuration de l'api</p>
	 * @param {Object} Configuration {@link jsocket.api.settings}
	 */
	configure: function(settings) {
		jsocket.api.settings = settings;
	},

	/**
	 * Selectionne un core
	 * @private
	 */
	setCore: function() {
		jsocket.api.method(jsocket.core.tcp);
	},

	/**
	 * <p>Deconnection du server via le core en cours.</p>
	 * @return {Boolean} True si la deconnection a reussie sinon False
	 */
	disconnect: function() {
		if (jsocket.api.core != null) {
			return (jsocket.api.core.close());
		}
		return (false);
	},

	/**
	 * <p>Changement de la methode de contact pour le serveur (par defaut TCP).</p>
	 *
	 * <p>Cores disponibles:
	 * <div class="mdetail-params"><ul>
	 * <li><b><tt>{@link jsocket.core.tcp#loaded}</tt></b></li>
	 * <li><b><tt>{@link jsocket.core.http#loaded}</tt></b></li>
	 * <li><b><tt>{@link jsocket.core.websocket#loaded}</tt></b></li>
	 * </ul></div></p>
	 * @param {Object} newCore La variable contenant le nouveau jsocketCore (tcp, http, websocket)
	 */
	method: function(newCore) {
		if (jsocket.api.core != null) {
			jsocket.api.disconnect();
			jsocket.api.core.isWorking = false;
			jsocket.api.core = newCore;
			jsocket.api.core.isWorking = true;
			jsocket.api.core.api = this;
			jsocket.api.core.connect();
		} else {
			jsocket.api.core = newCore;
			jsocket.api.core.isWorking = true;
			jsocket.api.core.api = this;
		}
	},

	/**
	 * <p>Enregistre une application dans l'API</p>
	 *
	 * <p><b><u>Exemple d'utilisation:</u></b></p>
<pre><code>
var myApplication = {
  onConnected: function(data) {
    if (data.value == true) {
	  alert('Vous etes connecte !');
	} else {
	  alert('La connection au serveur a echoue');
	}
  }
};
jsocket.api.register('myApplicationName', myApplication);
</code></pre>
	 * @param {String} appName Le nom de l'application
	 * @param {Object} appObject L'application contenant les callbacks
	 */
	register: function(appName, appObject) {
		var newApp = appObject || { };
		jsocket.api.app[appName] = newApp;
		jsocket.api.app[appName].isMaster = false;
	},

	/**
	 * @private
	 * Test si une application existe
	 * @param {String} appName Le nom de l'application
	 * @return {Boolean} True si l'application exists sinon False
	 */
	appExists: function(appName) {
		if (typeof(jsocket.api.app[appName]) != 'undefined') {
			return (true);
		}
		return (false);
	},

	/**
	 * @private
	 * Appel le callback (s'il existe) d'une application (si elle existe)
	 * @param {String} appName Le nom de l'application
	 * @param {String} callName Le nom du callback
	 * @return {Boolean} True si le callback a ete appele sinon False
	 */
	appCallback: function(appName, callName, args) {
		if (typeof(eval('jsocket.api.app["' + appName + '"].' + callName)) != 'undefined') {
			eval('jsocket.api.app["' + appName + '"].' + callName + '(args);');
			return (true);
		}
		return (false);
	},

	/**
	 * @private
	 * Appel le callback de chaque application
	 * @param {String} callName Le nom du callback
	 * @param {Mixed} args Les arguments a passer au callback
	 */
	appCallbacks: function(callName, args) {
		for (var i in jsocket.api.app) {
			jsocket.api.appCallback(i, callName, args);
		}
	},

	/**
	 * Active la console de debug de flash
	 * @param {Boolean} enable True pour activer la console False pour desactiver
	 */
	debug: function(enable) {
		if (jsocket.api.core.initialized == false) {
			setTimeout("jsocket.api.debug(" + enable + ");", 1000);
			return (false);
		}
		if (enable == true) {
			jsocket.api.debug = true;
			document.getElementById('socketBridge').style.top = '0px';
		}
		else {
			jsocket.api.debug = false;
			document.getElementById('socketBridge').style.top = '-1000px';
		}
	},

	/**
	 * @private
	 * Callback utilise pour transformer du texte en un objet JSON
	 * @param {String} text Le texte a transformer
	 */
	parser: function(text) {
		var j = JSON.parse(text);
		if (j.from != null && j.value != null) {
			func_name = j.from.substring(0, 1).toUpperCase() + j.from.substring(1, j.from.length);
			var args = { };
			args.value = (j.value != null ? j.value: '');
			args.channel = (j.channel != null ? j.channel: '');
			args.app = (j.app != null ? j.app: '');
			args = jsocket.api.core.stripslashes(args);
			if (j.app != null && j.app.length > 0 &&
				jsocket.api.appExists(j.app) == true) {
				try {
					jsocket.api.appCallback(args['app'], 'on' + func_name, args);
				} catch(e) { }
			}
			else {
				try {
					jsocket.api.appCallbacks('on' + func_name, args);
					eval('jsocket.api.on' + func_name + "(args)");
				} catch(e) {
					jsocket.api.onError(e);
				}
			}
		}
	},

	/**
	 * @private
	 * @event onConnected
	 * Callback utilise pour recevoir un identifiant par defaut lors de
	 * la connection au serveur.
	 * @param {Object} args Tableau contenant l'identifiant unique de l'utilisateur
	 */
	onConnected: function(args) {
		jsocket.api.uid = args.value;
		jsocket.api.sendPool();
	},

	/**
	 * @event onDisconnect
	 * Callback appele via flash quand la connection avec le serveur echoue
	 * @param {Object} args Objet ayant pour <i>value</i> un Boolean
	 */
	onDisconnect: function(args) {
	},

	/**
	 * @event onConnect
	 * Callback lorsque la connection avec le serveur est etablie.
	 * @param {Object} args Objet ayant pour <i>value</i> un Boolean
	 */
	onConnect: function(args) {
	},

	/**
	 * @private
	 * @event onReceive
	 * Callback utilise pour recevoir les donnees sortantes du serveur.
	 * @param {String} message Le message retourne par le serveur contenant une ou
	 * plusieurs commandes JSON. (Si plusieurs, elle sont alors separees par des \n)
	 */
	onReceive: function(message) {
		console.log('jsocket.api.receive: ', message);
		jsocket.api.parser(message);
	},

	/**
	 * @event onStatus
	 * Callback appele pour le master d'un channel lorsqu'un utilisateur
	 * quitte ou rejoind le channel.
	 * @param {Object} args Objet
	 */
	onStatus: function(args) {
	},

	/**
	 * @event onAuth
	 * Callback lorsque le serveur renvoie des informations suite a l'appel de la fonction auth
	 * @param {Object} args Objet ayant pour value le retour de l'appel a la methode auth
	 */
	onAuth: function(args) {
	},

	/**
	 * Cette fonction permet d'obtenir des droits supplementaire sur le serveur.
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 * @param {String} password Le mot de passe pour passer admin sur le serveur
	 */
	auth: function(appName, channel, password) {
		if (typeof(eval('jsocket.api.app["' + appName + '"]')) != 'undefined') {
			jsocket.api.app[appName].isMaster = true;
		}
		var json = {
			cmd: 'auth',
			args: password,
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * Authentifie un utilisateur (comme master) sur un channel
	 * @param {String} appName Le nom de l'application/channel
	 * @param {String} channel Le nom d'un salon
	 * @param {String} password Le mot de passe du channel
	 */
	chanAuth: function(appName, channel, password) {
		if (typeof(eval('jsocket.api.app["' + appName + '"]')) != 'undefined') {
			jsocket.api.app[appName].isMaster = true;
		}
		var json = {
			cmd: 'chanAuth',
			args: password,
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onChanAuth
	 * Callback lorsque le serveur renvoie des informations suite a l'appel de la fonction chanAuth
	 * @param {Object} args Channel password or false
	 */
	onChanAuth: function(args) {
	},

	/**
	 * @event onJoin
	 * Callback lorsque le serveur renvoie des informations suite a l'appel de la fonction join
	 * @param {Object} args Le retour de l'appel a la methode join
	 */
	onJoin: function(args) {
	},

	/**
	 * Cette fonction permet d'associé le client a un channel sur le serveur.
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 * @param {String} password Le mot de passe du salon
	 */
	join: function(appName, channel, password) {
		var json = {
			cmd: 'join',
			args: [ channel, password ],
			channel: channel,
			app: appName,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onPart
	 * Callback lorsque le serveur renvoie des informations suite a l'appel de la fonction part
	 * @param {Object} args Le retour de l'appel a la methode part
	 */
	onPart: function(args) {
	},

	/**
	 * Cette fonction permet de quitter le channel auquel le client est associé.
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 */
	part: function(appName, channel) {
		var json = {
			cmd: 'part',
			args: channel,
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onCreate
	 * Callback lorsque le serveur renvoie des informations suite a l'appel de la fonction create
	 * @param {Object} args Le retour de l'appel a la methode create
	 */
	onCreate: function(args) {
	},

	/**
	 * Cette fonction permet d'ajouter un nouveau channel sur le serveur.
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 * @param {String} password Le mot de passe du salon
	 */
	create: function(appName, channel, password) {
		if (typeof(eval('jsocket.api.app["' + appName + '"]')) != 'undefined') {
			jsocket.api.app[appName].isMaster = true;
		}
		var json = {
			cmd: 'create',
			args: [ channel, password ],
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onRemove
	 * Callback lorsque le serveur renvoie des informations suite a l'appel de la fonction remove
	 * @param {Object} args Le retour de l'appel a la methode remove
	 */
	onRemove: function(args) {
	},

	/**
	 * Cette fonction permet d'effacer un channel du serveur.
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 */
	remove: function(appName, channel) {
		var json = {
			cmd: 'remove',
			args: channel,
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * Change le nom de l'utilisateur courant
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 * @param {String} nickname Le nom d'utilisateur
	 */
	nick: function(appName, channel, nickname) {
		var json = {
			cmd: 'nick',
			args: nickname,
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onNick
	 * Callback lorsque le serveur renvoie des informations suite a
	 * l'appel de la fonction {@link #nick nick}
	 * @param {Object} args Le retour de l'appel a la methode {@link #nick nick}
	 */
	onNick: function(args) {
	},

	/**
	 * Cette fonction permet a un master de forwarder une commande
	 * sur tous les clients connectes a son channel
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 * @param {String} command La commande a forwarder
	 */
	forward: function(appName, channel, command) {
		var json = {
			cmd: 'forward',
			args: command,
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onForward
	 * Callback appeler lorsque un client recoie un message d'un master
	 * (via {@link #forward forward})
	 * @param {Object} args Le retour de la commande {@link #forward forward}
	 */
	onForward: function(args) {
	},

	/**
	 * Permet de lister tous les utilisateurs connecte au channel
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 */
	list: function(appName, channel) {
		var json = {
			cmd: 'list',
			args: channel,
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onList
	 * Callback appeler contenant la liste des utilisateurs connectes a un channel
	 * @param {Object} args Le retour de la commande {@link #list list}
	 */
	onList: function(args) {
	},

	/**
	 * Demande au serveur la liste des dernieres commandes effectuees par le master.
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 */
	history: function(appName, channel) {
		var json = {
			cmd: 'history',
			args: 'null',
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onHistory
	 * Callback appeler contenant la liste des dernieres commandes effectuees par le master.
	 * @param {Object} args Le retour de la commande {@link #history history}
	 */
	onHistory: function(args) {
	},

	/**
	 * Envoie un message a un ou plusieurs clients
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 * @param {Object} tab [0] = message a envoyer
	 *        [1] = [ '*' ] pour tous les clients du channel
	 *              [ '' ] ou [ 'master' ] pour le master du channel
	 *              [ 'username1', 'username2', 'uidClient3', ... ] pour une liste de clients
	 */
	message: function(appName, channel, tab) {
		var json = {
			cmd: 'message',
			args: tab,
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onMessage
	 * Callback reception d'un message {@link #message message}
	 * @param {Object} args command [0] = l'emmeteur du message
	 *        [1] = le message
	 */
	onMessage: function(args) {
	},

	/**
	 * Renvoie le statut de l'utilisateur courant
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 */
	getStatus: function(appName, channel) {
		var json = {
			cmd: 'getStatus',
			args: 'null',
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onGetStatus
	 * Callback reception status {@link #getStatus getStatus}
	 * @param {Object} args Status de l'utilisateur courant
	 */
	onGetStatus: function(args) {
	},

	/**
	 * Remplace le status de l'utilisateur courant
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 * @param {String} status Le status de l'utilisateur
	 */
	setStatus: function(appName, channel, status) {
		var json = {
			cmd: 'setStatus',
			args: status,
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onSetStatus
	 * Callback de la commande {@link #setStatus setStatus}
	 * @param {Object} args True or false
	 */
	onSetStatus: function(args) {
	},

	/**
	 * Renvoie l'heure a laquelle l'utilisateur courant s'est connecte
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 */
	timeConnect: function(appName, channel) {
		var json = {
			cmd: 'timeConnect',
			args: 'null',
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onTimeConnect
	 * Callback de la commande {@link #timeConnect timeConnect}
	 * @param {Object} args True or False
	 */
	onTimeConnect: function(args) {
	},

	/**
	 * Change le mot de passe d'un salon
	 * @param {String} appName Le nom de l'application
	 * @param {String} channel Le nom d'un salon
	 * @param {String} password Le mot de passe
	 */
	chanMasterPwd: function(appName, channel, password) {
		var json = {
			cmd: 'chanMasterPwd',
			args: password,
			app: appName,
			channel: channel,
			uid: 'jsocket.api.uid'
		};
		jsocket.api.send(jsocket.protocol.forge(json));
	},

	/**
	 * @event onChanMasterPwd
	 * Callback {@link #chanMasterPwd chanMasterPwd}
	 * @param {Object} args True or false
	 */
	onChanMasterPwd: function(args) {
	},

	/**
	 * @event onError
	 * Callback sur l'erreur d'execution d'une des methodes de l'API
	 * @param {String} error Le message d'erreur
	 */
	onError: function(error) {
	},

	/**
	 * @private
	 * @event onTCPError
	 * Callback sur l'erreur venant du core TCP. On change alors
	 * la methode de dialogue avec le serveur par HTTP.
	 * @param {String} error Le message d'erreur
	 */
	onTCPError: function(error) {
		if (jsocket.core.http.isWorking == false) {
			jsocket.api.method(jsocket.core.http);
			jsocket.api.init();
		}
	},

	/**
	 * @private
	 * Une fois que le client recupere son uid, alors les commandes
	 * en queue sont envoyes au serveur.
	 */
	sendPool: function() {
		for (var i = 0; i < jsocket.api.commands.length; ++i) {
			console.log('jsocket.api.send: ', jsocket.api.commands[i].replace(/jsocket\.api\.uid/, jsocket.api.uid));
			jsocket.api.core.send(jsocket.api.commands[i].replace(/jsocket\.api\.uid/, jsocket.api.uid));
		}
		jsocket.api.commands = [ ];
	},

	/**
	 * Gestion de queue pour les commandes a envoyer.
	 * Si jsocket.api.uid est null/empty alors on stock les
	 * commands puis on les envoie lorsque l'uid est renseigne.
	 * @param {String} msg Le message (commande JSON) a envoyer
	 */
	send: function(msg) {
		if (jsocket.api.uid != '') {
			console.log('jsocket.api.send: ', msg.replace(/jsocket\.api\.uid/, jsocket.api.uid));
			jsocket.api.core.send(msg.replace(/jsocket\.api\.uid/, jsocket.api.uid));
		} else if (jsocket.api.commands.length < 10) {
			jsocket.api.commands.push(msg);
		}
	}
};

/**
 * Includes swf for flash socket bridge
 */
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
