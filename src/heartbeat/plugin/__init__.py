from queue import Queue
import importlib

class ModuleLoader(object):

    def load_multiple(paths, full_classpath=False):
        modules = []
        for p in paths:
            modules.append(ModuleLoader.load_module(p, full_classpath))

        return modules

    def load(path, full_classpath=False):
        if full_classpath:
            path = ".".join(path.split(".")[:-1])

        module = importlib.import_module(path)
        return module


class PluginRegistry(type):

    plugins = {}

    def __init__(cls, name, bases, attrs):
        if name != 'Plugin':
            PluginRegistry.plugins[cls.__module__ + "." + name] = cls


class Plugin(object, metaclass=PluginRegistry):

    work_queue = None

    def queue_work(self, work):
        self.work_queue.put(work)

    def get_signal_hook(self, signal):
        return None

