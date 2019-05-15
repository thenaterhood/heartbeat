import datetime
import json
import inspect
import os
import sys
from enum import Enum
import logging
from time import time
import hashlib
import uuid
import yaml
from pathlib import Path

__config_manager = None


class Topics(Enum):

    """
    Event types
    """
    WARNING = "error"
    INFO = "information"
    DEBUG = "debug"
    VIRT = "virtual"
    HEARTBEAT = "heartbeat"
    STARTUP = "startup"
    # @since v3.12.0
    ACK = "acknowledge"


class Event(object):

    """
    An event to notify of. Contains a title, message, and timestamp
    """
    __slots__ = ('title', 'message', 'timestamp', 'host',
                 'one_time', 'source', 'payload', 'type', 'when', 'id')

    def __init__(self, title, message, host="localhost", type=None):
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
        self.id = str(uuid.uuid4())
        if (type is None):
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
        dictionary['id'] = self.id

        return json.dumps(dictionary)

    def from_json(jsonString):
        try:
            dictionary = json.loads(jsonString)
        except Exception:
            raise Exception('Malformed event JSON')

        if not 'title' in dictionary or \
            not 'message' in dictionary or \
            not 'type' in dictionary:
                raise Exception('Event missing required fields')

        try:
            Topics[dictionary['type']]
        except KeyError:
            raise Exception('Unsupported event type')

        e = Event(
            title=dictionary['title'],
            message=dictionary['message'],
            host=dictionary['host'] if 'host' in dictionary else 'localhost',
            type=Topics[dictionary['type']]
            )
        e.one_time = dictionary['one_time'] if 'one_time' in dictionary else False
        e.source = dictionary['source'] if 'source' in dictionary else 'Unknown'

        if ('payload' in dictionary):
            e.payload = dictionary['payload']
        else:
            e.payload = {}

        # legacy support
        if ('id' in dictionary):
            e.id = dictionary['id']
        else:
            e.id = str(uuid.uuid4())

        return e

    def __str__(self):
        return (self.title + ": " + self.host) + ((": " + self.message) if self.message else "")

class ConfigManager:
    __slots__ = ('__config', '__finalized')

    def __init__(self, entries):
        self.__config = entries
        self.__finalized = False

    def __getattr__(self, prop):
        try:
            if isinstance(self.__config[prop], dict):
                cfg_manager = ConfigManager(self.__config[prop])
                cfg_manager.finalize()
                return cfg_manager
            else:
                return self.__config[prop]
        except:
            return None

    def __contains__(self, prop):
        return prop in self.__config

    def add_item(self, prop, value):
        if self.__finalized:
            raise Exception("Adding items to a finalized configuration is not allowed")
        else:
            self.__config[prop] = value

    def finalize(self):
        self.__finalized = True

def _get_config_path(path = None):
    if (path is not None):
        return path

    root_path = '/'
    if 'PROGRAMDATA' in os.environ:
        root_path = os.path.join(os.environ['PROGRAMDATA'], 'Heartbeat')

    paths = [
            os.path.join(os.path.expanduser('~'), '.heartbeat'),
            os.path.join(root_path, 'usr', 'local', 'etc', 'heartbeat'),
            os.path.join(root_path, 'etc', 'heartbeat')
            ]

    for p in paths:
        if os.path.exists(p):
            return p

    raise Exception("No configuration path found. Have you run `heartbeat-install`?")

def get_cache_path(settings=None):
    if settings is None:
        settings = get_config_manager()

    cache_path = settings.heartbeat.cache_dir

    if not os.access(cache_path, os.W_OK):
        print("No access to cache path, using user directory")
        cache_path = os.path.join(
                os.path.expanduser('~'),
                '.cache',
                'heartbeat'
                )
        if not os.path.exists(cache_path):
            try:
                os.makedirs(cache_path, exist_ok=True)
            except Exception:
                pass

    return cache_path


def get_config_manager(path = None):

    global __config_manager

    if __config_manager is not None:
        return __config_manager

    print("Getting config manager")
    config_dir = _get_config_path(path)
    cfg_manager = ConfigManager({
        'heartbeat': {
            'monitor_server': None,
            'plugins': {},
            'query_interval': 60,
            'log_dir': '/var/log'
        }
    })

    if not os.path.exists(config_dir) or  not os.path.exists(os.path.join(config_dir, "heartbeat.conf")):
        raise Exception("Configuration data could not be found. You can install the base configuration for Heartbeat using `heartbeat-install --install-cfg`")

    confdir = Path(config_dir)
    conf_list = [f for f in confdir.resolve().glob('**/*') if f.is_file()]
    for conffile in conf_list:
        # In Python < 3.6, the Path objects need to be converted to str
        # or Python gets upset.
        with open(str(conffile)) as f:
            conf_key = os.path.splitext(os.path.basename(str(conffile)))[0]
            cfg_manager.add_item(conf_key, yaml.safe_load(f))

    cfg_manager.finalize()
    __config_manager = cfg_manager

    return cfg_manager
