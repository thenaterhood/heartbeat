import importlib
import yaml


class Configuration():

    __slots__ = ('config', 'notifiers', 'hwmonitors')

    def __init__(self, configFile='/etc/heartbeat.yml', load_modules=False):
        stream = open(configFile, 'r')
        self.config = yaml.load(stream)
        stream.close()

        self.notifiers = []
        self.hwmonitors = []

        if (load_modules):
            self.load_notifiers()
            self.load_hwmonitors()

    def load_notifiers(self):
        if (self.config['notifiers'] is None):
            return []
        for n in self.config['notifiers']:
            modulepath = "heartbeat.notifiers." + ".".join(n.split(".")[:-1])
            module = importlib.import_module(modulepath)
            self.notifiers.append(getattr(module, n.split(".")[-1]))

        return self.notifiers

    def load_hwmonitors(self):
        if (self.config['monitors'] is None):
            return []
        for m in self.config['monitors']:
            modulepath = "heartbeat.hwmonitors." + ".".join(m.split(".")[:-1])
            module = importlib.import_module(modulepath)
            self.hwmonitors.append(getattr(module, m.split(".")[-1]))

        return self.hwmonitors
