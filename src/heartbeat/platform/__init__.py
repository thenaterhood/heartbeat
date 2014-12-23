import datetime
import json
import inspect
import importlib
import yaml


class Event:

    """
    An event to notify of. Contains a title, message, and timestamp
    """
    __slots__ = ('title', 'message', 'timestamp', 'host', 'one_time', 'source', 'payload')

    def __init__(self, title='', message='', host="localhost"):
        """
        Constructor

        Params:
            string title:   the title of the event
            string message: the message describing the event
        """
        self.title = title
        self.message = message
        self.timestamp = datetime.datetime.now()
        self.host = host
        self.payload = {}
        self.one_time = False
        stack = inspect.stack()
        self.source = str(stack[1][0].f_locals["self"].__class__.__name__)

    def __hash__(self):
        return hash((self.title, self.message, self.source, self.host))

    def to_json(self):
        dictionary = dict()
        dictionary['title'] = self.title
        dictionary['message'] = self.message
        dictionary['host'] = self.host
        dictionary['one_time'] = self.one_time
        dictionary['source'] = self.source
        dictionary['payload'] = self.payload

        return json.dumps(dictionary)

    def load_json(self, jsonString):
        dictionary = json.loads(jsonString)

        self.title = dictionary['title']
        self.message = dictionary['message']
        self.host = dictionary['host']
        self.one_time = dictionary['one_time']
        self.source = dictionary['source']
        if ('payload' in dictionary):
            self.payload = dictionary['payload']
        else:
            self.payload = {}

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
            modulepath = "heartbeat.monitoring." + ".".join(m.split(".")[:-1])
            module = importlib.import_module(modulepath)
            self.hwmonitors.append(getattr(module, m.split(".")[-1]))

        return self.hwmonitors
