from notifiers import pushbullet
from hwmonitors import smartctl

# The secret identifying key for this particular monitor/heartbeat.
# Use the same key for all the heartbeats monitored by the same monitor
SECRET_KEY = '3477'

# The port to use for sending and receiving packets
PORT = 21999

# Set to true if this device should have a heartbeat
HEARTBEAT = True

# Set to true if this device is monitoring. Note that the
# device can have both a heartbeat and a monitor, though
# it will ignore its own heartbeat
MONITOR = True

# The notifiers for when a new heartbeat is discovered or when a host
# flatlines. Must also be imported.
NOTIFIERS = [
    pushbullet.pushbullet
]

# Set this to true to enable hardware monitoring using
# the monitors configured below. This will use the same
# notifiers, which accept an Event object. These need
# to be imported similar to the notifiers
ENABLE_HWMON = True

HW_MONITORS = [
    smartctl.SMARTMonitor
]
