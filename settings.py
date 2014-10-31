from notifiers import pushbullet

# The secret identifying key for this particular monitor/heartbeat.
# Use the same key for all the heartbeats monitored by the same monitor
SECRET_KEY = '3477'

# The port to use for sending and receiving packets
PORT = 21999

# The notifiers for when a new heartbeat is discovered or when a host
# flatlines. Must also be imported.
NOTIFIERS = [
    pushbullet.pushbullet
]
