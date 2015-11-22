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

	def get_worker(self, worker_id):
		return None

	def get_signal_hook(self, signal):
		return None