heartbeat
============
Heartbeat is a dead simple network monitoring tool. Set it up, run the
heartbeat.py script on the servers to monitor, and the monitor.py script on
a server to keep track of things. It will send a notification whenever a new
heartbeat is detected, whenever a host appears to flatline, or when a
hardware monitor reports an error.

How
============
Network broadcast packets.

Setup
============
If you're on ArchLinux, a pkgbuild is provided with the occasional package
in the releases under the releases tab here on Github.

Once installed, configure a port and secret string in the settings.py file or
in the /etc/heartbeat.conf depending on your install. This is used
for the monitor to identify heartbeats so that multiple heartbeats can be
on the same network with different monitors.

Import and add notify scripts to the NOTIFIERS array. Any time a new heartbeat
is detected or an existing heartbeat disappears, heartbeat will push a
notification to the configured notifiers.

Heartbeat is modular and can be used with any combination of its modules,
currently hardware monitoring, heartbeat, and a heartbeat monitor. These can
be enabled or disabled in the settings.py file. For a heartbeat and the
associated monitor of it, make sure to configure the SECRET_KEY and PORT
settings, which respectively give a heartbeat a distinct signature and the
port to operate on. Multiple heartbeats can coexist on the same network
by using unique ports or secret keys.

Notifiers
============
Right now only pushbullet, dweetio and the builtin histamine. More will be a
thing eventually. Make one? drop it in the notifiers directory with some brief
instructions and put in a pull if you feel inclined to share.

While heartbeat can be used in a decentralized way by configuring notifiers
for each individual node, it can also be used with a central monitoring node.
To use heartbeat with a central node, enable the Histamine notifier in
the settings (histamine.Histamine) and enable histamine in the server settings.
Histamine will broadcast notification events from a node which will be
received by any histamine server on the network using a matching secret key.
Histamine nodes will forward the notification to all the configured notifiers.

Using a notifier:
* Add it to the NOTIFIERS array, without the heartbeat.notifiers path prefix

Hardware Monitors
============
Heartbeat is also capable of notifying of hardware changes or problems with
added hardware monitors. They use the same notification framework as
heartbeat for new/flatlined hosts.

Using a hardware monitor:
* Add it to the HW_MONITORS array, without the heartbeat.hwmonitors path prefix

Roadmap
============
This started as a means of learning some basic socket fun and python threading.
Next up for this:

- Code cleanup. Things can probably be reworked and written better.
- More notifiers.
- Better security (make the secret string actually secret)
- Remember the devices on the network to avoid the "found a new heartbeat" spam
 when starting the monitor - DONE!
- Potentially, more features (but seriously, dead simple can be nice)

License
============
Included software is distributed under the BSD 3-clause license. See LICENSE
for full license text.

Though not required by the license terms, please consider contributing,
providing feedback, or simply dropping a line to say that this software was
useful to you. Pull requests are always welcome.

