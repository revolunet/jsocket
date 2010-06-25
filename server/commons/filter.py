"""
* FILTRES COMMANDES FORWARD :

* SUPPRIMER TOUT :
   this.scene.sendClientSize*
   this.scene.setCursor*
   this.scene.YT_*
   this.scene.VP_*
   this.scene.toggleWebcam*
   window.open*

* Garder seulement les lignes apres le dernier:
   this.scene.addImage*

* conserver l'ordre des commandes
"""
import re

class Filter(object):
	"""
	Class pour filtrer l'historique, via des regexp.
	"""
	def __init__(self):
		self.__filters = []
		self.init_filters()

	def init_filters(self):
		"""
		Liste des filtres pour l'history.
		"""

		self.__filters.append({ 'name': 'sendClientSize', 'match' : r"""this.scene.sendClientSize""",
			'handler' : self.remove
		})
		self.__filters.append({ 'name': 'setCursor', 'match' : r"""this.scene.setCursor""",
			'handler' : self.remove
		})
		self.__filters.append({ 'name': 'YT_', 'match' : r"""this.scene.YT_""",
			'handler' : self.remove
		})
		self.__filters.append({ 'name': 'VP_', 'match' : r"""this.scene.VP_""",
			'handler' : self.remove
		})
		self.__filters.append({ 'name': 'toggleWebcam', 'match' : r"""this.scene.toggleWebcam""",
			'handler' : self.remove
		})
		self.__filters.append({ 'name': 'window.open', 'match' : r"""window.open""",
			'handler' : self.remove
		})
		self.__filters.append({ 'name': 'addImage', 'match' : r"""this.scene.addImage""",
			'handler' : self.untilLast
		})

	def Run(self, history):
		"""
		Filtre un historique en appliquant les regexp des filtres.
		"""

		filter_history = history
		for filter in self.__filters:
			method = filter.get('handler', None)
			match = filter.get('match', None)
			if method is not None:
				filter_history = method(filter_history, match)
		return filter_history

	def remove(self, history, match):
		"""
		Remove methode sur les commande de l'historique.
		Si le pattern match on supprime le record.
		"""

		filter_history = []
		for h in history:
			if re.search(match, h.get('json'), re.MULTILINE | re.DOTALL) is None:
				filter_history.append(h)
		return filter_history

	def untilLast(self, history, match):
		"""
		Delete les lignes de l'historique qui match les filtres sauf le dernier record
		"""

		toDelete = []
		for h in history:
			if re.search(match, h.get('json'), re.MULTILINE | re.DOTALL) is not None:
				toDelete.append(h)
		toDelete = toDelete[:-1]
		for delete in toDelete:
			history.pop(history.index(delete))
		return history
