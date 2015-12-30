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
    whitelist = []

    def __init__(cls, name, bases, attrs):
        full_class = cls.__module__ + "." + name
        if name != 'Plugin' and full_class in PluginRegistry.whitelist:
            PluginRegistry.plugins[cls.__module__ + "." + name] = cls

    def filter_by_package(package):

        filtered = {}

        for pkg, c in PluginRegistry.plugins.items():
            if pkg.startswith(package):
                filtered[pkg] = c

        return filtered


class Plugin(object, metaclass=PluginRegistry):

    work_queue = None

    def queue_work(self, work):
        self.work_queue.put(work)

    def get_signal_hook(self, signal):
        return None
