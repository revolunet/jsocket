import sys
import traceback

class JException(object):
	class JException_:
		"""
		Static method, handle sur les Exceptions avec plus de detail.
		"""
		
		def __init__(self):
			pass

		def formatExceptionInfo(maxTBlevel=5):
			cla, exc, trbk = sys.exc_info()
			excName = cla.__name__
			try:
				excArgs = exc.__dict__["args"]
			except KeyError:
				excArgs = "<no args>"
			excTb = traceback.format_tb(trbk, maxTBlevel)
			return (excName, excArgs, excTb)
		
	instance = None
		
	def __new__(c):
		if not JException.instance:
			JException.instance = JException.JException_()
		return JException.instance
		
	def __getattr__(self, attr):
		return getattr(self.instance, attr)
		
	def __setattr__(self, attr, val):
		return setattr(self.instance, attr, val)