import datetime
import json
import inspect
import importlib
import yaml
from enum import Enum
import logging


class EventType(Enum):

    """
    Event types
    """
    WARNING = "error"
    INFO = "information"
    DEBUG = "debug"

class Event:

    """
    An event to notify of. Contains a title, message, and timestamp
    """
    __slots__ = ('title', 'message', 'timestamp', 'host', 'one_time', 'source', 'payload', 'type')

    def __init__(self, title='', message='', host="localhost", type=None):
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
        if (type == None):
            self.type = EventType.INFO
        else:
            if (not isinstance(self.type, EventType)):
                raise Exception("type passed to Event is not an EventType")
            self.type = type
        stack = inspect.stack()
        self.source = str(stack[1][0].f_locals["self"].__class__.__name__)

    def __hash__(self):
        return hash((self.title, self.message, self.source, self.host, self.type))

    def to_json(self):
        dictionary = dict()
        dictionary['title'] = self.title
        dictionary['message'] = self.message
        dictionary['host'] = self.host
        dictionary['one_time'] = self.one_time
        dictionary['source'] = self.source
        dictionary['payload'] = self.payload
        dictionary['type'] = self.type.name

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
        self.type = EventType[dictionary['type']]

class Autoloader():

    __slots__ = ("modules", "paths", "_logger")

    def __init__(self, paths = []):
        self._logger = logging.getLogger(__name__ + "." + "Autoloader")
        self.paths = paths
        self.modules = []
        self._logger.debug("Autoloader primed")

    def load(self):
        for p in self.paths:
            self.loadPath(p)

    def loadPath(self, path):
        modulepath = ".".join(path.split(".")[:-1])
        self._logger.debug("Importing module " + modulepath)
        module = importlib.import_module(modulepath)
        self.modules.append(getattr(module, path.split(".")[-1]))
        if (path not in self.paths):
            self.paths.append(path)

class Configuration():

    def __init__(self, configFile='/etc/heartbeat.yml', load_modules=False):
        self._logger = logging.getLogger(__name__ + "." + "Configuration")

        self._logger.debug("Loading configuration file " + configFile)
        stream = open(configFile, 'r')
        self.config_data = yaml.load(stream)
        stream.close()

        self.notifiers = []
        self.hwmonitors = []

        if (load_modules):
            self._logger.debug("Loading configured modules")
            self.load_notifiers()
            self.load_hwmonitors()

    def __getattr__(self, attr):
        if (attr in self.config_data):
            return self.config_data[attr]
        elif (attr == "config"):
            return self.config_data
        else:
            raise AttributeError("Configuration does not contain " + attr)

    def load_notifiers(self):

        if (self.config['notifiers'] is None):
            return []

        loader = Autoloader()
        for n in self.config['notifiers']:
            modulepath = "heartbeat.notifications." + ".".join(n.split("."))
            loader.loadPath(modulepath)

        self.notifiers = loader.modules
        return self.notifiers

    def load_hwmonitors(self):
        if (self.config['monitors'] is None):
            return []

        loader = Autoloader()
        for m in self.config['monitors']:
            modulepath = "heartbeat.monitoring." + ".".join(m.split("."))
            loader.loadPath(modulepath)

        self.hwmonitors = loader.modules
        return self.hwmonitors
