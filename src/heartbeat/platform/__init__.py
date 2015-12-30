import datetime
import json
import inspect
import importlib
import os
import sys
import yaml
from enum import Enum
import logging
from pymlconf import ConfigManager
from heartbeat.plugin import ModuleLoader, PluginRegistry


class Topics(Enum):

    """
    Event types
    """
    WARNING = "error"
    INFO = "information"
    DEBUG = "debug"
    VIRT = "virtual"
    HEARTBEAT = "heartbeat"


class Event(object):

    """
    An event to notify of. Contains a title, message, and timestamp
    """
    __slots__ = ('title', 'message', 'timestamp', 'host',
                 'one_time', 'source', 'payload', 'type')

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
            self.type = Topics.INFO
        else:
            if (not isinstance(self.type, Topics)):
                raise Exception("Topic received was not recognized")
            self.type = type
        stack = inspect.stack()

        try:
            self.source = str(stack[1][0].f_locals["self"].__class__.__name__)
        except KeyError:
            self.source = None

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

    def from_json(jsonString):
        dictionary = json.loads(jsonString)

        e = Event()
        e.title = dictionary['title']
        e.message = dictionary['message']
        e.host = dictionary['host']
        e.one_time = dictionary['one_time']
        e.source = dictionary['source']
        if ('payload' in dictionary):
            e.payload = dictionary['payload']
        else:
            e.payload = {}
        e.type = Topics[dictionary['type']]

        return e

    def __str__(self):
        return self.title + ": " + self.host + ": " + self.message


def _translate_legacy_config(config_file, config_skeleton):

    with open(config_file, 'r') as stream:
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

                if (not element in config_location):
                    config_location[element] = {}

                config_location = config_location[element]
            for setting in y[key].keys():
                config_location[setting] = y[key][setting]

    return config_skeleton

def _get_config_path(path = None):
    if (path is not None):
        return path
    elif (sys.platform == 'win32'):
        return os.path.join(os.environ['PROGRAMDATA'], 'Heartbeat', 'Settings')
    else:
        linux_paths = [
                os.path.join(os.path.expanduser('~'), '.heartbeat'),
                os.path.join('/', 'usr', 'local', 'etc', 'heartbeat'),
                os.path.join('/', 'etc', 'heartbeat')
                ]

        for p in linux_paths:
            if os.path.exists(p):
                return p

        return os.path.join('/', 'etc', 'heartbeat')


def get_config_manager(path = None):

    config_dir = _get_config_path(path)

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
            (config_dir + '.yml'),
            _default_config
        )

        cfg = ConfigManager(config_dict, [], [])

    else:
        cfg = ConfigManager(_default_config, [config_dir])

    return cfg


def load_trusted_plugins(modules, package='', full_classpath=True):

    for m in modules:
        modulepath = ".".join([package] + m.split("."))
        PluginRegistry.whitelist.append(modulepath)
        ModuleLoader.load(modulepath, full_classpath)

def load_notifiers(notifiers):

    load_trusted_plugins(notifiers, package="heartbeat.notifications")
    return PluginRegistry.filter_by_package("heartbeat.notifications").values()


def load_monitors(monitors):

    load_trusted_plugins(monitors, package="heartbeat.monitoring")
    return PluginRegistry.filter_by_package("heartbeat.monitoring").values()
