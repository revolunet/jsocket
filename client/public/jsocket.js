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

if (typeof console == 'undefined') {
	console = {
		log: function() { },
		error: function() { }
	};
}

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
 * @class jsocket.utils
 * <p><b><u>jsocket utils</u></b></p>
 * <p>Valide et forge le JSON des commandes a partir d'un objet.</p>
 * @author Revolunet
 * @version 0.3.0
 * @singleton
 */
jsocket.utils = {
	/**
	 * Forge une commande JSON a partir d'un objet javascript
	 * @param {Object} obj Objet javascript
	 * @return {String} Commande JSON
	 */
	forge: function(obj) {
		for (var i in obj) {
			obj[i] = this.addslashes(obj[i]);
		}
		return (JSON.stringify(obj));
	},

	/**
	 * Addslashes les caracteres ' " \\ \0
	 * @param {String} str Le texte a addslasher
	 * @return {String} La chaine avec les caracteres echapes
	 */
	addslashes: function(str) {
		if (typeof str == 'string') {
			str = encodeURIComponent(str);
			str = str.replace(/\'/g, "%27");
		} else if (typeof str == 'object') {
			for (var i in str) {
				str[i] = this.addslashes(str[i]);
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
		if (typeof str == 'string') {
			str = str.replace(/\%27/g, "'");
			str = decodeURIComponent(str);
		} else if (typeof str == 'object') {
			for (var i in str) {
				str[i] = this.stripslashes(str[i]);
			}
		}
		return (str);
	},

    /**
     * Force scope of given function
     * @param {function} fn Function
     * @param {Object} obj Scope
     * @param {mixed} args (optional) Arguments
     * @return {function} Delegated function
     */
    createDelegate: function(fn, obj, args) {
        if (typeof fn != 'function') {
            return fn;
        }
        return function() {
            var callArgs = args || arguments;
            if (typeof callArgs != 'object') {
                callArgs = [];
            }
            return fn.apply(obj || window, callArgs);
        };
    },

    /**
     * Defer function calling by given millis.
     * @param {function} fn Function
     * @param {Integer} millis Milliseconds
     * @param {Object} obj Scope
     * @param {mixed} args (optional) Arguments
     * @return {Integer} Result
     */
    defer: function(fn, millis, obj, args) {
        fn = this.createDelegate(fn, obj, args);
        if (millis > 0) {
            return setTimeout(fn, millis);
        }
        fn();
        return 0;
    }
};

/**
 * @class jsocket.core.tcp
 * Javascript event's interface for flash swf socket bridge
 * @author Revolunet
 * @version 0.3.0
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
	available: false,

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
     * True si le flash a appele le callback de load.
     * @private
     * @type Boolean
     */
    isLoaded: false,

    /**
     * Core name
     * @private
     * @type String
     */
    name: 'tcp',

    /**
     * Last try date time
     * @private
     * @type Integer
     */
    lastTry: false,

    /**
     * Flag lorsque la connection est ferme manuellement
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
        this.isLoaded = true;
		this.connectedToServer = false;
		this.socket = document.getElementById("socketBridge");
		this.output = document.getElementById("jsocketBridgeOutput");
		return (true);
	},

    /**
     * Retourne true si le core TCP est disponible, false sinon.
     * @return {Boolean} True si le core TCP est disponible, sinon false
     */
    isAvailable: function() {
        if (typeof navigator != 'undefined' &&
            typeof navigator.mimeTypes != 'undefined' &&
            typeof navigator.mimeTypes['application/x-shockwave-flash'] != 'undefined' &&
            navigator.mimeTypes["application/x-shockwave-flash"].enabledPlugin != null) {
            this.available = true;
        } else if (window.ActiveXObject) {
            try {
                var a = new ActiveXObject("ShockwaveFlash.ShockwaveFlash");
                this.available = true;
            } catch (oError) {
                this.available = false;
            }
        } else {
            this.available = false;
        }
        return (this.available);
    },

	/**
	 * Initialise une connection via une socket sur le server:port
	 */
	connect: function() {
        if (this.lastTry == false) {
            this.lastTry = new Date().getTime();
        }
        if (this.available == false) {
            this.api.parser(jsocket.utils.forge({from: 'TCPError',
                                                 value: 'TCP is not available'}));
            return (false);
        }
        if (new Date().getTime() - this.lastTry > 2000) {
            this.api.parser(jsocket.utils.forge({from: 'TCPError',
                                                 value: 'TCP is not available'}));
            return (false);
        }
		if (this.isLoaded == true &&
            this.connectedToServer == false) {
			this.socket.connect(this.api.settings.tcp.host, this.api.settings.tcp.port);
		} else if (this.connectedToServer == false) {
			this.setTimeout(this.connect, 500);
		}
        return (true);
	},

	/**
	 * Lance un setTimeout sur cmd avec comme temps d'attente delay a
	 * condition que ce core est utilise par l'API
	 * @param {String} cmd La commande a lancer
	 * @param {Int} delay Le temps d'attente
	 */
	setTimeout: function(method, delay, args) {
		if (this.isWorking == true) {
            if (args) {
                jsocket.utils.defer(method, delay, this, args);
            } else {
                jsocket.utils.defer(method, delay, this);
            }
		}
	},

	/**
	 * Envoie le message au serveur.
	 * Tentative de reconnection a ce dernier le cas echeant.
	 * @param {String} msg Le texte a envoyer au serveur
	 * @return {Boolean} True si le message a ete envoye sinon False
	 */
	write: function(msg) {
		if (this.connectedToServer == false) {
			this.connect();
		}
		if (this.connectedToServer) {
			this.socket.write(msg + "\n");
		} else {
			this.setTimeout(this.send, 500, msg);
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
		return (this.write(msg));
	},

	/**
	 * @event connected
	 * Callback appele par flash lorsque la socket est connectee au serveur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	connected: function() {
        this.lastTry = false;
		this.connectedToServer = true;
        this.keepAlive();

        this.send('{ "cmd": "connected", "args": { "vhost": "' + this.api.settings.vhost + '" }}');

		return (true);
	},

    /**
     * Send keep alive request to server to prevent watchdog to delete client.
     */
    keepAlive: function() {
        if (this.connectedToServer && this.isWorking) {
            this.api.send(jsocket.utils.forge({cmd: 'keepalive',
                                               uid: '.uid.'}));
        }
        if (this.isWorking) {
            this.setTimeout(this.keepAlive, this.api.settings.keepAliveTimer);
        }
    },

	/**
	 * Ferme la connection au serveur
	 * @return {Boolean} True si la connection a ete fermee sinon False
	 */
	close: function() {
        if (this.socket) {
            this.manuallyDisconnected = true;
            this.socket.close();
            this.disconnected();
        }
		return (true);
	},

	/**
	 * @event disconnected
	 * Callback appele par flash lorsqu'une deconnection a ete effectuee
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	disconnected: function() {
		this.api.uid = '';
		this.api.parser(jsocket.utils.forge({from: 'disconnect', value: true}));
        if (this.connectedToServer == false) {
            return (false);
        }
		this.connectedToServer = false;
        if (this.manuallyDisconnected == true) {
            this.manuallyDisconnected = false;
        } else {
            this.connect();
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
		this.api.parser(jsocket.utils.forge({from: 'error', value: msg}));
		if (this.connectedToServer == false) {
			this.api.parser(jsocket.utils.forge({from: 'TCPError', value: 'Input/Output error'}));
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
		this.api.parser(jsocket.utils.forge({from: 'error', value: msg}));
		if (this.connectedToServer == false) {
			this.api.parser(jsocket.utils.forge({from: 'TCPError', value: 'Security error'}));
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
		var tab = decodeURIComponent(msg).split("\n");
		for (var i = 0; i < tab.length; ++i) {
			this.api.onReceive(tab[i]);
		}
		return (true);
	}
};

/**
 * @class jsocket.core.http
 * Javascript event's interface fail over HTTP
 * @author Revolunet
 * @version 0.3.0
 * @singleton
 */
jsocket.core.http = {
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
	available: false,

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
	commands: [],

	/**
	 * True si ce core est utilise par l'API sinon False
	 * @private
	 * @type Boolean
	 */
	isWorking: false,

    /**
     * Core name
     * @private
     * @type String
     */
    name: 'http',

	/**
	 * Return true si le core HTTP est disponible, sinon false.
	 * @return {Boolean} True si le code HTTP est disponible, sinon false
	 */
	isAvailable: function()	{
		this.available = true;
		return (this.available);
	},

    /**
     * Permet d'effectuer une request HTTP GET sur le server (host, port)
     * @param {String} parameters La commande JSON a envoyee
     * @return {Boolean} True si la commande a ete envoyee sinon False
     */
    _get: function(parameters) {
        parameters = encodeURI('json=' + parameters);
        var el = document.createElement('script');
        el.type = 'text/javascript';
        el.onload = this.receive;
        el.onreadystatechange = this.receive;
        el.src = this.api.settings.http.url + '?' + parameters + '&ts=' + new Date().getTime();
        document.body.appendChild(el);
		this.response.waiting = true;
        return (true);
    },

	/**
	 * Initialise une connection via une socket sur le server:port
	 */
	connect: function() {
        if (this.connectedToServer == true) {
            return (false);
        }

        this._get('{ "cmd": "connected", "args": { "vhost": "' + this.api.settings.vhost + '" }}');

		this.pool();
        this.response.waiting = false;
        return (true);
	},

	/**
	 * Pool le serveur HTTP en envoyant les requetes des n dernieres
	 * secondes du client et pour obtenir les reponses des commandes
	 * actuelles/precedentes
	 * @return {Boolean} False si l'API n'est pas definie
	 */
	pool: function() {
		if (this.isWorking == false) {
			return (false);
		}
        if (this.connectedToServer == true) {
            this.write();
        }
		jsocket.utils.defer(this.pool, this.api.settings.http.refreshTimer, this);
	},

	/**
	 * Ferme la connection au serveur
	 * @return {Boolean} True si la connection a ete fermee sinon False
	 */
	close: function() {
		this.connectedToServer = false;
        this._get(jsocket.utils.forge({
                    cmd: 'disconnected',
                    uid: this.api.uid}));
		return (true);
	},

	/**
	 * Verifie si une commande peut etre envoye au serveur
	 * @return {Boolean} True si la commande peut etre envoyee sinon False
	 */
	checkResponse: function() {
		var now = Math.floor(new Date().getTime() / 1000);
		if (this.response.waiting == false) {
			return (true);
		} else if ((now - this.response.lastTime) > this.response.timeout) {
			this.response.lastTime = now;
			return (true);
		}
		return (false);
	},

	/**
	 * Envoie les commandes stockees prealablement au serveur.
	 * @return {Boolean} True si les commandes ont ete envoyees sinon False
	 */
	write: function() {
		if (this.checkResponse() == false) {
			return (false);
		}
		msg = '';
		if (this.commands.length > 0) {
			msg = this.commands.join("\n");
			this.commands = [];
            this._get(msg + "\n");
		} else {
            this._get(jsocket.utils.forge({
                        cmd: 'refresh',
                        uid: this.api.uid}));
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
			return (this.commands.push(msg));
		}
		return (false);
	},

	/**
	 * @event connected
	 * Callback appele par flash lorsque la socket est connectee au serveur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	connected: function() {
		this.connectedToServer = true;
		return (true);
	},

	/**
	 * @event disconnected
	 * Callback appele par flash lorsqu'une deconnection a ete effectuee
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	disconnected: function() {
		this.api.parser(jsocket.utils.forge({from: 'disconnect', value: true}));
		this.connectedToServer = false;
		this.connect();
		return (true);
	},

	/**
	 * @event receive
	 * Callback appele par socket lors de la reception d'un message
	 * @return {Boolean} True si la commande a ete envoyee a l'API sinon False
	 */
    receive: function() {
        if (this.readyState &&
            (this.readyState == "loaded" ||
             this.readyState == "complete") &&
            this.parentNode) {
            this.parentNode.removeChild(this);
        } else if (this.readyState != "loading" && this.parentNode) {
            this.parentNode.removeChild(this);
        }
		if (typeof jsocket.core.http.api != 'object') {
			return (false);
		}
        if (jsocket.core.http.connectedToServer == false) {
            jsocket.core.http.connected();
        }
        jsocket.core.http.response.waiting = false;
        jsocket.core.http.response.lastTime = Math.floor(new Date().getTime() / 1000);
		return (true);
    }
};

/**
 * @class jsocket.core.websocket
 * Javascript event's interface for websocket HTML 5
 * @author Revolunet
 * @version 0.3.0
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
    available: false,

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
     * Core name
     * @private
     * @type String
     */
    name: 'websocket',

    /**
     * Last connection try time
     * @private
     * @type Boolean
     */
    lastTry: false,

	/**
	 * Retourne true si le core websocket est disponible, false sinon.
	 * @return {Boolean} True si le core websocket est disponible sinon false
	 */
	isAvailable: function() {
		if ('WebSocket' in window) {
			this.available = true;
		} else {
            this.available = false;
        }
		return (this.available);
	},

	/**
	 * Initialise une connection via une socket sur le server:port
	 */
	connect: function() {
        if (this.lastTry == false) {
            this.lastTry = new Date().getTime();
        }
		if (this.available == false) {
			this.api.parser(jsocket.utils.forge({from: 'WebSocketError',
                                                 value: 'WebSocket not available'}));
			return (false);
		}
        if (new Date().getTime() - this.lastTry > 2000) {
            this.api.parser(jsocket.utils.forge({from: 'WebSocketError',
                                                 value: 'WebSocket connect timeout'}));
            return (false);
        }
        if (this.socket == null) {
            this.socket = new WebSocket('ws://' + this.api.settings.websocket.host +
                                        ':' + this.api.settings.websocket.port + '/jsocket');
            this.socket.onmessage = jsocket.utils.createDelegate(this.receive, this);
            this.socket.onerror = jsocket.utils.createDelegate(this.error, this);
            this.socket.onopen = jsocket.utils.createDelegate(this.connected, this);
            this.socket.onclose = jsocket.utils.createDelegate(this.disconnected, this);
        } else if (this.connectedToServer == false) {
            this.setTimeout(this.connect, 500);
        }
        return (true);
	},

	/**
	 * @event connected
	 * Callback appele par flash lorsque la socket est connectee au serveur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	connected: function() {
        this.lastTry = false;
		this.connectedToServer = true;
        this.keepAlive();
		this.socket.send('{ "cmd": "connected", "args": { "vhost": "' + this.api.settings.vhost + '" }}');
		return (true);
	},

    /**
     * Send keep alive request to server to prevent watchdog to delete client.
     */
    keepAlive: function() {
        if (this.connectedToServer && this.isWorking) {
            this.api.send(jsocket.utils.forge({
                        cmd: 'keepalive',
                        uid: '.uid.'}));
        }
        if (this.isWorking) {
            this.setTimeout(this.keepAlive, this.api.settings.keepAliveTimer);
        }
    },

	/**
	 * Ferme la connection au serveur
	 * @return {Boolean} True si la connection a ete fermee sinon False
	 */
	close: function() {
		if (this.socket) {
			this.manuallyDisconnected = true;
            this.socket.close();
        }
		return (true);
	},

	/**
	 * @event disconnected
	 * Callback appele par flash lorsqu'une deconnection a ete effectuee
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	disconnected: function() {
        if (this.socket) {
            delete this.socket;
        }
		this.api.uid = '';
		this.api.parser(jsocket.utils.forge({from: 'disconnect', value: true}));
		if (this.connectedToServer == false) {
			return (false);
		}
		this.connectedToServer = false;
		if (this.manuallyDisconnected == true) {
			this.manuallyDisconnected = false;
		} else {
			this.connect();
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
		this.api.parser(jsocket.utils.forge({from: 'WebSocketError', value: msg}));
		return (true);
	},

	/**
	 * @event receive
	 * Callback appele par WebSocket lors de la reception d'un message
	 * @param {String} msg Le message envoye par le serveur
	 * @return {Boolean} False si le core n'est pas attache a l'API sinon True
	 */
	receive: function(msg) {
		msg = msg.data;
		var tab = msg.split("\n");
		for (var i = 0; i < tab.length; ++i) {
			this.api.onReceive(tab[i]);
		}
		return (true);
	},

	/**
	 * Lance un setTimeout sur cmd avec comme temps d'attente delay a
	 * condition que ce core est utilise par l'API
	 * @param {String} cmd La commande a lancer
	 * @param {Int} delay Le temps d'attente
	 */
	setTimeout: function(method, delay, args) {
		if (this.isWorking == true) {
            if (args) {
                jsocket.utils.defer(method, delay, this, args);
            } else {
                jsocket.utils.defer(method, delay, this);
            }
		}
	},

	/**
	 * Envoie le message au serveur.
	 * Tentative de reconnection a ce dernier le cas echeant.
	 * @param {String} msg Le texte a envoyer au serveur
	 * @return {Boolean} True si le message a ete envoye sinon False
	 */
	write: function(msg) {
		if (this.connectedToServer == false) {
			this.connect();
		}
		if (this.connectedToServer) {
			this.socket.send(msg + "\n");
		} else {
			this.setTimeout(this.send, 500, msg);
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
		return (this.write(msg));
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
 * @version 0.3.0
 * @singleton
 */
jsocket.api = {
	/**
	 * Le core a utiliser par defaut
	 * @private
	 * @type {Object}
	 */
	core: null,

	/**
	 * A activer pour afficher les commandes JSON en entree/sortie
	 * @private
	 * @type {Boolean}
	 */
	isDebug: false,

	/**
	 * Le tableau des applications enregistrees dans l'API
	 * @private
	 * @type {Object}
	 */
	app: {},

	/**
	 * L'uid du client une fois connecte
	 * @public
	 * @type {String}
	 */
	uid: '',

	/**
	 * La liste des commandes en attente d'envoie
	 * @private
	 * @type {Array}
	 */
	commands: [],

	/**
	 * <p>Parametres de configuration:</p>
	 * <p><div class="mdetail-params"><ul>
	 * <li><b><tt>tcp.host: Host pour le core {@link jsocket.core.tcp#isAvailable}</tt></b></li>
	 * <li><b><tt>tcp.port: Port pour le core {@link jsocket.core.tcp#isAvailable}</tt></b></li>
	 * <li><b><tt>http.url: Url pour le core {@link jsocket.core.http#isAvailable}</tt></b></li>
	 * <li><b><tt>http.refreshTimer: Temps entre chaque rafraichissement (en ms) pour le core {@link jsocket.core.http#isAvailable}</tt></b></li>
	 * <li><b><tt>websocket.host: Host pour le core {@link jsocket.core.websocket#isAvailable}</tt></b></li>
	 * <li><b><tt>websocket.port: Port pour le core {@link jsocket.core.websocket#isAvailable}</tt></b></li>
	 * <li><b><tt>vhost (optional): Vhost</tt></b></li>
	 * <li><b><tt>keepAliveTimer: Timer pour le keepalive</tt></b></li>
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
    url: 'http://localhost:8081/',
	refreshTimer: 1000
  },
  websocket: {
    host: 'localhost',
    port: 8082
  },
  vhost:'test.quickprez.com',
  keepAliveTimer: 60000
};
</code></pre>
	 */
	settings: {
		tcp: {
			host: 'localhost',
			port: 8080
		},
		http: {
			url: 'http://localhost:8081/',
			refreshTimer: 1000
		},
		websocket: {
			host: 'localhost',
			port: 8082
		},
        vhost:'',
        keepAliveTimer: 60000
	},

	/**
	 * <p>Connection au serveur via le jsocket.core</p>
	 * @param {Object} Parametre optionnel de configuration {@link jsocket.api.settings}
	 */
	connect: function(settings) {
		if (typeof settings != 'undefined' && settings != null) {
			this.configure(settings);
		}
		if (this.core == null) {
            this.setCore();
		} else {
            this.method(this.core);
        }
	},

	/**
	 * <p>Permet de changer la configuration de l'api</p>
	 * <p>La configuration donnee en parametre peut etre partielle mais doit
	 * tout de meme respecter l'arborescence de {@link jsocket.api.settings}<p>
	 * @param {Object} Configuration {@link jsocket.api.settings}
	 */
	configure: function(settings) {
		for (core in this.settings) {
			if (typeof settings[core] == 'object') {
				for (opt in this.settings[core]) {
					if (typeof settings[core][opt] != 'undefined') {
						this.settings[core][opt] = settings[core][opt];
					}
				}
			}
            else if (typeof settings[core] == 'string') {
                this.settings[core] = settings[core];
            }
		}
	},

	/**
	 * Selectionne un core
	 * @private
	 */
	setCore: function() {
        if (jsocket.core.websocket.isAvailable() == true) {
            this.method(jsocket.core.websocket);
        } else if (jsocket.core.tcp.isAvailable() == true) {
            this.method(jsocket.core.tcp);
        } else {
            this.method(jsocket.core.http);
        }
	},

	/**
	 * <p>Deconnection du server via le core en cours.</p>
	 * @return {Boolean} True si la deconnection a reussie sinon False
	 */
	disconnect: function() {
		if (typeof this.core != 'undefined' &&
            this.core && this.core.close() == true) {
            this.uid = '';
            return (true);
		}
		return (false);
	},

	/**
	 * <p>Changement de la methode de contact pour le serveur (par defaut TCP).</p>
	 *
	 * <p>Cores disponibles:
	 * <div class="mdetail-params"><ul>
	 * <li><b><tt>{@link jsocket.core.tcp#isAvailable}</tt></b></li>
	 * <li><b><tt>{@link jsocket.core.http#isAvailable}</tt></b></li>
	 * <li><b><tt>{@link jsocket.core.websocket#isAvailable}</tt></b></li>
	 * </ul></div></p>
	 * @param {Object} newCore La variable contenant le nouveau jsocketCore (tcp, http, websocket)
	 */
	method: function(newCore) {
        if (this.isDebug) {
            console.log('[jsocket-api] method: ', newCore, newCore.name);
        }
        if (newCore.isAvailable() == false) {
            newCore = jsocket.core.http;
        }
		if (this.core != null) {
            if (this.core.connectedToServer == true) {
                this.disconnect();
            }
            if (this.core != newCore) {
                this.uid = '';
                this.core.isWorking = false;
                this.core = newCore;
                this.core.isWorking = true;
                this.core.api = this;
            }
            if (this.core.connectedToServer == false) {
                this.core.connect();
            }
		} else {
			this.core = newCore;
			this.core.isWorking = true;
			this.core.api = this;
            if (this.core.connectedToServer == false) {
                this.core.connect();
            }
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
		var newApp = appObject || {};
		this.app[appName] = newApp;
		this.app[appName].isMaster = false;
		if (typeof this.app[appName].onHistory == 'undefined') {
			this.app[appName].onHistory = this.onHistory;
		}
	},

	/**
	 * @private
	 * Test si une application existe
	 * @param {String} appName Le nom de l'application
	 * @return {Boolean} True si l'application exists sinon False
	 */
	appExists: function(appName) {
		if (typeof(this.app[appName]) != 'undefined') {
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
		if (typeof this.app[appName][callName] != 'undefined') {
			this.app[appName][callName](args);
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
		for (var appName in this.app) {
			this.appCallback(appName, callName, args);
		}
	},

	/**
	 * Active la console de debug de flash
	 * @param {Boolean} enable True pour activer la console False pour desactiver
	 */
	debug: function(enable) {
		if (this.core.isAvailable() == false) {
			jsocket.utils.defer(this.debug, 1000, this, enable);
			return (false);
		}
		if (enable == true) {
			this.isDebug = true;
            if (document.getElementById('socketBridge')) {
                document.getElementById('socketBridge').style.top = '0px';
            }
		}
		else {
			this.isDebug = false;
            if (document.getElementById('socketBridge')) {
                document.getElementById('socketBridge').style.top = '-1000px';
            }
		}
	},

	/**
	 * @private
	 * Callback utilise pour transformer du texte en un objet JSON
	 * @param {String} text Le texte a transformer
	 */
	parser: function(text) {
        if (this.isDebug) {
            console.log('[jsocket-api] receive: ', text);
        }
		var j = {};
		try {
			j = JSON.parse(text);
		} catch (e) {
			return (false);
		}
		if (j.from != null && j.value != null) {
			func_name = 'on' + j.from.substring(0, 1).toUpperCase() + j.from.substring(1, j.from.length);
			var args = {
                value: (j.value ? j.value : ''),
                channel: (j.channel ? j.channel : ''),
                app: (j.app ? j.app : '')
            };
			if (j.from == 'history') {
				args.channel = jsocket.utils.stripslashes(args.channel);
				args.app = jsocket.utils.stripslashes(args.app);
			} else {
				args = jsocket.utils.stripslashes(args);
			}
			if (j.app != null && j.app.length > 0 &&
				this.appExists(j.app) == true) {
				try {
					this.appCallback(args['app'], func_name, args);
				} catch(e) {
					return (this.onError(e));
				}
			} else {
				try {
					this.appCallbacks(func_name, args);
					this[func_name].call(this, args);
				} catch(e) {
					return (this.onError(e));
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
		this.uid = args.value;
		this.sendPool();
		this.onReceive('{"from": "connect", "value": true}');
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
		this.parser(message);
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
		if (typeof this.app[appName] != 'undefined') {
			this.app[appName].isMaster = true;
		}
		var json = {
			cmd: 'auth',
			args: password,
			app: appName,
			channel: channel,
			uid: '.uid.'
		};
		this.send(jsocket.utils.forge(json));
	},

	/**
	 * Authentifie un utilisateur (comme master) sur un channel
	 * @param {String} appName Le nom de l'application/channel
	 * @param {String} channel Le nom d'un salon
	 * @param {String} password Le mot de passe du channel
	 */
	chanAuth: function(appName, channel, password) {
		if (typeof this.app[appName] != 'undefined') {
			this.app[appName].isMaster = true;
		}
		var json = {
			cmd: 'chanAuth',
			args: password,
			app: appName,
			channel: channel,
			uid: '.uid.'
		};
		this.send(jsocket.utils.forge(json));
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
			uid: '.uid.'
		};
		this.send(jsocket.utils.forge(json));
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
			uid: '.uid.'
		};
		this.send(jsocket.utils.forge(json));
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
		if (typeof this.app[appName] != 'undefined') {
			this.app[appName].isMaster = true;
		}
		var json = {
			cmd: 'create',
			args: [ channel, password ],
			app: appName,
			channel: channel,
			uid: '.uid.'
		};
		this.send(jsocket.utils.forge(json));
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
			uid: '.uid.'
		};
		this.send(jsocket.utils.forge(json));
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
			uid: '.uid.'
		};
		this.send(jsocket.utils.forge(json));
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
			uid: '.uid.'
		};
		this.send(jsocket.utils.forge(json));
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
			uid: '.uid.'
		};
		this.send(jsocket.utils.forge(json));
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
			uid: '.uid.'
		};
		this.send(jsocket.utils.forge(json));
	},

	/**
	 * @event onHistory
	 * <p>Callback appeler contenant la liste des dernieres commandes effectuees par le master.
	 * Toutes les commandes recues en value seront alors repassee au parser de l'API (et donc
	 * les callbacks du client correspondant aux commandes seront rappeles).</p>
	 * <p>Si par defaut une interface n'a pas cet evenement d'implementer, c'est celui de l'API
	 * qui lui sera affectee.</p>
	 * @param {Object} args Le retour de la commande {@link #history history}
	 */
	onHistory: function(args) {
		var values = args.value;
		var length = values.length;
		if (!(typeof values == 'object' && length > 0)) {
			return (false);
		}
		for (var i in values) {
			if (typeof values[i]['json'] != 'undefined') {
				var cmd = values[i]['json'].replace(/\%27/g, "'");
				cmd = decodeURIComponent(cmd);
				this.parser(cmd);
			}
		}
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
			uid: '.uid.'
		};
		this.send(jsocket.utils.forge(json));
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
			uid: '.uid.'
		};
		this.send(jsocket.utils.forge(json));
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
			uid: '.uid.'
		};
		this.send(jsocket.utils.forge(json));
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
			uid: '.uid.'
		};
		this.send(jsocket.utils.forge(json));
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
			uid: '.uid.'
		};
		this.send(jsocket.utils.forge(json));
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
	 * @event onWebSocketError
	 * Callback sur l'erreur venant du core WebSocket. On change
	 * alors la methode de dialogue avec le serveur par TCP.
	 */
	onWebSocketError: function() {
        if (jsocket.core.tcp.isAvailable() == true &&
            jsocket.core.tcp.isWorking == false) {
            this.method(jsocket.core.tcp);
        } else if (jsocket.core.http.isWorking == false) {
            this.method(jsocket.core.http);
        }
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
			this.method(jsocket.core.http);
		}
	},

	/**
	 * @private
	 * Une fois que le client recupere son uid, alors les commandes
	 * en queue sont envoyes au serveur.
	 */
	sendPool: function() {
		for (var i = 0; i < this.commands.length; ++i) {
			this.core.send(this.commands[i].replace(/\.uid\./, this.uid));
		}
		this.commands = [];
	},

	/**
	 * Gestion de queue pour les commandes a envoyer.
	 * Si this.uid est null/empty alors on stock les
	 * commands puis on les envoie lorsque l'uid est renseigne.
	 * @param {String} msg Le message (commande JSON) a envoyer
	 */
	send: function(msg) {
        if (this.isDebug) {
            console.log('[jsocket-api] send: ', msg);
        }
		if (this.uid != '') {
			this.core.send(msg.replace(/\.uid\./, this.uid));
		} else if (this.commands.length < 10) {
			this.commands.push(msg);
		}
	}
};

/**
 * Includes swf for flash socket bridge
 */
function createSwf() {
	if (typeof swfobject != 'undefined' && typeof jsocket.core.tcp != 'undefined') {
		swfobject.embedSWF(jsocketBridgeDomain, "flashcontent", "900", "200", "8.0.0", "expressInstall.swf",
						   {scope: 'jsocket.core.tcp', AllowScriptAccess:'always'}, {menu: false, AllowScriptAccess:'always'},
						   {id:'socketBridge', name:'socketBridge', style:'position:absolute;top:-1000px;', AllowScriptAccess:'always'});
	} else {
		setTimeout('createSwf()', 200);
	}
}

createSwf();
