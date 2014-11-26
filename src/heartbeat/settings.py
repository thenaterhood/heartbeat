import configparser
import importlib

config = configparser.ConfigParser()
config.read('/etc/heartbeat.conf')

SECRET_KEY = config['basic']['secret_key']
PORT = int(config['basic']['port'])
NOTIFIERS = []
HW_MONITORS = []
HEARTBEAT_CACHE_DIR = config['basic']['cache_dir']

for key, value in config.items("notifiers"):
    modulepath = "heartbeat.notifiers." + ".".join(value.split(".")[:-1])
    module = importlib.import_module(modulepath)
    NOTIFIERS.append(getattr(module, value.split(".")[-1]))

for key, value in config.items("hwmonitors"):
    modulepath = "heartbeat.hwmonitors." + ".".join(value.split(".")[:-1])
    module = importlib.import_module(modulepath)
    HW_MONITORS.append(getattr(module, value.split(".")[-1]))

# Set to true if this device should have a heartbeat
HEARTBEAT = config['services']['heartbeat']

# Set to true if this device is monitoring. Note that the
# device can have both a heartbeat and a monitor, though
# it will ignore its own heartbeat
MONITOR = config['services']['monitor']

# Set this to true to enable hardware monitoring using
# the monitors configured below. This will use the same
# notifiers, which accept an Event object. These need
# to be imported similar to the notifiers
ENABLE_HWMON = config['services']['hwmonitor']

ENABLE_HISTAMINE = config['services']['histamine']
