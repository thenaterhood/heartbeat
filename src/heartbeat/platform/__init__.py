import datetime
import json
import inspect
import importlib
import os
import yaml
from enum import Enum
import logging
from pymlconf import ConfigManager

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

    def __str__(self):
        return self.title + ": " + self.host + ": " + self.message

class Autoloader():

    __slots__ = ("modules", "paths", "_logger")

    def __init__(self, paths = []):
        self._logger = logging.getLogger(
                __name__ + "." + self.__class__.__name__
                )
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

def _translate_legacy_config(config_file, config_skeleton):

    stream = open(config_file, 'r')
    y = yaml.load(stream)

    for key in y.keys():
        if (not '.' in key):
            config_skeleton['heartbeat'][key] = y[key]

        else:
            path = key.split('.')
            if path[0] == 'heartbeat':
                path = path[1:]
            if path[0] == 'hwmonitors':
                path[0] = 'monitors'

            config_location = config_skeleton

            for element in path:
                if (element == "notifiers"):
                    element = "notifying"

                if (element == "monitors"):
                    element = "monitoring"
                config_location[element] = {}
                config_location = config_location[element]
            for setting in y[key].keys():
                config_location[setting] = y[key][setting]

    return config_skeleton


def get_config_manager(config_dir='/etc/heartbeat', config_file='/etc/heartbeat.yml'):

    _default_config = {
            'heartbeat': {
                'monitor_server': None
                },
            'notifiers': {
                },
            'monitors': {
                }
            }

    if (not os.path.exists(config_dir)):
        config_dict = _translate_legacy_config(
                config_file,
                _default_config
                )

        cfg = ConfigManager(config_dict, [], [])

    else:
        cfg = ConfigManager(_default_config, [config_dir])

    return cfg

def load_notifiers(notifiers):

    if (notifiers is None):
        return []

    loader = Autoloader()
    for n in notifiers:
        modulepath = "heartbeat.notifications." + ".".join(n.split("."))
        loader.loadPath(modulepath)

    notifiers = loader.modules
    return notifiers

def load_monitors(monitors):
    if (monitors is None):
        return []

    loader = Autoloader()
    for m in monitors:
        modulepath = "heartbeat.monitoring." + ".".join(m.split("."))
        loader.loadPath(modulepath)

    hwmonitors = loader.modules
    return hwmonitors
