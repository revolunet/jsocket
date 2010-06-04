/**
 * @class jsocket.protocol
 * <p><b><u>jsocket Protocol</u></b></p>
 * <p>Valide et forge le JSON des commandes a partir d'un objet.</p>
 * @author Revolunet
 * @version 0.2.3
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
