from Queue import Queue


class ModuleLoader(object):

	def load_multiple(paths):
		modules = []
		for p in paths:
			modules.append(ModuleLoader.load_module(p))
			
		return modules

	def load_path(path):
		module = importlib.import_module(module_path)
		return module


class PluginRegistry(type):

	plugins = []

	def __init__(cls, name, bases, attrs):
		if name != 'Plugin':
			PluginRegistry.plugins.append(cls)
			

class Plugin(object):
	__metaclass__ = PluginRegistry

	work_queue = None

	def queue_work(self, work):
		self.work_queue.put(work)

	def get_signal_hook(self, signal):
		return None
