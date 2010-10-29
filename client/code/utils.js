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
	forge : function(obj) {
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
		}
		else if (typeof str == 'object') {
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
		}
		else if (typeof str == 'object') {
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
