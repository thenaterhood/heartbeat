import datetime
import json
import inspect
import os
import sys
import yaml
from enum import Enum
import logging
from pymlconf import ConfigManager
from time import time
import hashlib


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
                 'one_time', 'source', 'payload', 'type', 'when')

    def __init__(self, title='', message='', host="localhost", type=None):
        """
        Constructor

        Params:
            string title:   the title of the event
            string message: the message describing the event
        """
        self.title = title
        self.message = message
        self.when = time()
        self.timestamp = datetime.datetime.fromtimestamp(self.when)
        self.host = host
        self.payload = {}
        self.one_time = False
        if (type == None):
            self.type = Topics.INFO
        else:
            if (not isinstance(type, Topics)):
                raise Exception("Topic received was not recognized")
            self.type = type
        stack = inspect.stack()

        try:
            self.source = str(stack[1][0].f_locals["self"].__class__.__name__)
        except KeyError:
            self.source = None

    def __hash__(self):
        as_bytes = (self.title + self.message + self.source + self.host + self.type.name).encode("UTF-8")

        return hashlib.sha512(as_bytes).hexdigest()

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

def _get_config_path(path = None):
    if (path is not None):
        return path
    elif (sys.platform == 'win32'):
        return os.path.join(os.environ['PROGRAMDATA'], 'Heartbeat', 'etc', 'heartbeat')
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
            'monitor_server': None,
            'plugins': {}
        }
    }

    if not os.path.exists(config_dir) or  not os.path.exists(os.path.join(config_dir, "heartbeat.conf")):
        raise Exception("Configuration data could not be found. You can install the base configuration for Heartbeat using `heartbeat-install --install-cfg`")

    cfg = ConfigManager(_default_config, [config_dir])

    return cfg
