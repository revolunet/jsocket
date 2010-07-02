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
			'handler' : self.remove, 'type': 'in'
		})
		self.__filters.append({ 'name': 'setCursor', 'match' : r"""this.scene.setCursor""",
			'handler' : self.remove, 'type': 'in'
		})
		self.__filters.append({ 'name': 'YT_', 'match' : r"""this.scene.YT_""",
			'handler' : self.remove, 'type': 'in'
		})
		self.__filters.append({ 'name': 'VP_', 'match' : r"""this.scene.VP_""",
			'handler' : self.remove, 'type': 'in'
		})
		self.__filters.append({ 'name': 'toggleWebcam', 'match' : r"""this.scene.toggleWebcam""",
			'handler' : self.remove, 'type': 'in'
		})
		self.__filters.append({ 'name': 'window.open', 'match' : r"""window.open""",
			'handler' : self.remove, 'type': 'in'
		})
		self.__filters.append({ 'name': 'gotRemoteSize', 'match' : r"""this.scene.gotRemoteSize""",
			'handler' : self.remove, 'type': 'in'
		})
		self.__filters.append({ 'name': 'addImage', 'match' : r"""this.scene.addImage""",
			'handler' : self.removeTo, 'type': 'out'
		})

	def Run(self, history):
		"""
		Filtre un historique en appliquant les regexp des filtres.
		"""

		filter_history = history
		for filter in self.__filters:
			method = filter.get('handler', None)
			match = filter.get('match', None)
			inout = filter.get('type', None)
			if method is not None and inout is not None and inout == 'out':
				filter_history = method(filter_history, match)
		return filter_history

	def RunIn(self, cmd):
		"""
		Filtre les commandes en entree d historique
		"""
		import time

		json_cmd = {'json': cmd, 'time': time.time(), 'uid': None}
		filter_history = []
		filter_history.append(json_cmd)
		for filter in self.__filters:
			method = filter.get('handler', None)
			match = filter.get('match', None)
			inout = filter.get('type', None)
			if method is not None and inout is not None and inout == 'in':
				filter_history = method(filter_history, match)
		if len(filter_history) == 1:
			return True
		return False


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
		index = None
		for h in history:
			if re.search(match, h.get('json'), re.MULTILINE | re.DOTALL) is not None:
				toDelete.append(h)
		if toDelete:
			toDelete = toDelete[:-1]
			for delete in toDelete:
				index = history.index(delete)		
				if index is not None:
					history.pop(index)
		return history

	def removeTo(self, history, match):
		"""
		Efface tous l'historique jusqu'a la derniere occurence de match
		"""
		index = None
		toDelete = []
		for h in history:
			if re.search(match, h.get('json'), re.MULTILINE | re.DOTALL) is not None:
				toDelete.append(h)
		if toDelete:
			toDelete = toDelete[-1]
			index = history.index(toDelete)
		if index is not None:
			return history[index:]
		return history
