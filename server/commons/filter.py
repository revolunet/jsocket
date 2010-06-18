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
		self.__filters.append({ 'name': 'sendClientSize', 'match' : 'this.scene.sendClientSize',
			'handler' : self.remove
		})
		self.__filters.append({ 'name': 'setCursor', 'match' : 'this.scene.setCursor',
			'handler' : self.remove
		})
		self.__filters.append({ 'name': 'YT_', 'match' : 'this.scene.YT_',
			'handler' : self.remove
		})
		self.__filters.append({ 'name': 'VP_', 'match' : 'this.scene.VP_',
			'handler' : self.remove
		})
		self.__filters.append({ 'name': 'toggleWebcam', 'match' : 'this.scene.toggleWebcam',
			'handler' : self.remove
		})
		self.__filters.append({ 'name': 'addImage', 'match' : 'this.scene.addImage',
			'handler' : self.untilLast
		})
		
	def Run(self, history):
		filter_history = history
		for filter in self.__filters:
			method = filter.get('handler', None)
			match = filter.get('match', None)
			if method is not None:
				filter_history = method(filter_history, match)
		return filter_history
				
	def remove(self, history, match):
		filter_history = []
		for h in history:
			if re.match(h.get('json'), match) is None:
				filter_history.append(h)
		return filter_history
		
	def untilLast(self, history, match):
		toDelete = []
		for h in history:
			if re.match(h.get('json'), match) is not None:
				toDelete(h)
		toDelete = toDelete[:-1]
		for delete in toDelete:
			history.pop(history.index(delete))
		return history