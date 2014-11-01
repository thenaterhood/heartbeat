heartbeat
============
Heartbeat is a dead simple network monitoring tool. Set it up, run the
heartbeat.py script on the servers to monitor, and the monitor.py script on
a server to keep track of things. It will send a notification whenever a new
heartbeat is detected and whenever a host appears to flatline.

How
============
Network broadcast packets.

Setup
============
Configure a port and secret string in the settings.py file. This is used
for the monitor to identify heartbeats so that multiple heartbeats can be
on the same network with different monitors.

Import and add notify scripts to the NOTIFIERS array. Any time a new heartbeat
is detected or an existing heartbeat disappears, heartbeat will push a
notification to the configured notifiers.

Notifiers
============
Right now only pushbullet. More will be a thing. Make one? drop it in the
notifiers directory with some brief instructions and put in a pull if you
feel inclined to share.

Roadmap
============
This started as a means of learning some basic socket fun and python threading.
Next up for this:

-Code cleanup. Things can probably be reworked and written better.
-More notifiers.
-Better security (make the secret string actually secret)
-Remember the devices on the network to avoid the "found a new heartbeat" spam
 when starting the monitor
-Potentially, more features (but seriously, dead simple can be nice)

License
============
Included software is distributed under the BSD 3-clause license. See LICENSE
for full license text.

Though not required by the license terms, please consider contributing,
providing feedback, or simply dropping a line to say that this software was
useful to you. Pull requests are always welcome.

