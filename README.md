heartbeat
============

What Heartbeat is
-------------
Heartbeat is a dead simple network monitoring tool. Set it up, start it with
your init system (systemd or sysvinit), or manually with the `startheart`
command. It will send a notification whenever a new heartbeat is detected,
whenever a host appears to flatline, or when a hardware monitor reports an
error. It is designed for quick notifications if problems happen, geared
towards a relatively small fleet of servers.

What Heartbeat is NOT
-------------
Heartbeat is NOT intended to be used as a full-fledged monitoring, management,
or logging tool. Rather, it is a tiny application intended to provide another,
extremely lightweight method of keeping tabs on servers with minimal overhead.
Tools like Nagios and Observium require a database and keep track of much
more information over time, which Heartbeat is not designed to do.

How
============
Network broadcast packets and threading.

Setup
============
If you're on ArchLinux, a pkgbuild is provided with the occasional package
in the releases under the releases tab here on Github.

If you're not on ArchLinux, you can build and install the package using make. By default, heartbeat will be configured assuming that systemd is the system init system. To use sysvinit instead, run make with the argument INIT_SYSTEM=sysvinit, which will instead set up heartbeat with an init script. To manually build and install the package, run:

        make [[BUILD_PATH=build-heartbeat] INIT_SYSTEM=sysvinit]
        sudo make [[[BUILD_PATH=build-heartbeat] INSTALL_PATH=/] PRESERVE_CFG=no] install

The BUILD_PATH, INIT_SYSTEM, and INSTALL_PATH are optional parameters. The make
install command MUST use the same BUILD_PATH value as the make command. The
PRESERVE_CFG will check for and avoid overwriting an existing configuration on
install if specified as yes.

Once installed, configure a port and secret string in the /etc/heartbeat.yml
file. This is used for the monitor to identify heartbeats so that multiple
heartbeats can be on the same network with different monitors.

See the [wiki](https://github.com/thenaterhood/heartbeat/wiki/Configuration)
and the inline comments in the
[/etc/heartbeat.yml](https://github.com/thenaterhood/heartbeat/blob/master/dist/_etc/heartbeat.yml)
file for more detailed setup instructions.

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

Also see [the wiki](https://github.com/thenaterhood/heartbeat/wiki/Notifiers)

Hardware Monitors
============
Heartbeat is also capable of notifying of hardware changes or problems with
added hardware monitors. They use the same notification framework as
heartbeat for new/flatlined hosts.

Also see [the wiki](https://github.com/thenaterhood/heartbeat/wiki/Monitoring)

License
============
Included software is distributed under the BSD 3-clause license. See LICENSE
for full license text.

Though not required by the license terms, please consider contributing,
providing feedback, or simply dropping a line to say that this software was
useful to you. Pull requests are always welcome.

