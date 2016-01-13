heartbeat
============
[![Build Status](https://travis-ci.org/thenaterhood/heartbeat.svg?branch=master)](https://travis-ci.org/thenaterhood/heartbeat)
[![Code Climate](https://codeclimate.com/github/thenaterhood/heartbeat/badges/gpa.svg)](https://codeclimate.com/github/thenaterhood/heartbeat)
[![Code Health](https://landscape.io/github/thenaterhood/heartbeat/master/landscape.svg?style=flat)](https://landscape.io/github/thenaterhood/heartbeat/master)
[![Codacy Badge](https://api.codacy.com/project/badge/grade/d2ed1f70fd774c6f9111a96b12d8dcac)](https://www.codacy.com/app/thenaterhood/heartbeat)

Heartbeat is a super simple and minimalistic plugin-based monitoring and
notification tool. Heartbeat comes with a handful of monitoring and notification
plugins and provides a simple API for developing your own.

Heartbeat is intended to be highly flexible and adaptable to suit various
applications. The core of Heartbeat is designed for asynchronous routing of
information from producers (which can be anything) to handlers (which can
also be anything). Heartbeat can be used for anything from monitoring a fleet
of servers to developing an IoT system. The PubSub architecture in Heartbeat
allows the same Heartbeat community to send information to both humans and
other computers, without stepping on each others' toes.

Heartbeat is not designed with huge-scale systems in mind. Although Heartbeat
can, in theory, handle such situations, it has not been tested that way. Heartbeat
provides basic security for encrypting data in transit over a network, but has
not been tested for security thoroughly; use Heartbeat at your own risk.

# Usage
Heartbeat supports Linux and Linux-like operating systems running Python 3.2
and newer. Support for Windows is in progress, but is still experimental.

## Installation
Heartbeat can be installed directly through Python using the provided setup.py
file in the repository. Installing Heartbeat through this requires setuptools
to be installed but should otherwise work on any platform Python is able to
run on. Once the repository is cloned to a local location, you can install
Heartbeat by running `python setup.py install`

For ArchLinux users, a pkgbuild is available in the repository for those
interested in building their own package, and a pre-built package installable
with pacman is provided with each release. Some manual intervention may be
required to install Heartbeat's requirements, as some are not available in
the AUR or Arch repositories. You can install a pre-built package by running
`sudo pacman -U heartbeat-<your_version>.pkg.xz`.

For Windows users, an experimental installer generated using setuptools is
provided with most releases. This installer will not install Heartbeat's
dependencies, so manual intervention is required. All of Heartbeat's
dependencies are available through pip.

After installing, you will need to use the Heartbeat helper script to install
at a minimum, Heartbeat's base configuration files, and service files if
desired. Run `heartbeat-install --install-cfg`, and `heartbeat-install --help`
to see more options.

For more information about installing and configuring Heartbeat, visit the Wiki:
[installation](https://github.com/thenaterhood/heartbeat/wiki/Installation) and
[configuration](https://github.com/thenaterhood/heartbeat/wiki/Configuration).

## Using Heartbeat
Heartbeat should be configured prior to use. See the [configuration information](https://github.com/thenaterhood/heartbeat/wiki/Configuration) and
[list of provided plugins](https://github.com/thenaterhood/heartbeat/wiki/Packaged-Plugins)

On all platforms, Heartbeat can be started manually by issuing the command
`startheart`. Depending on your needs and the plugins you're using, you may
need to grant Heartbeat root access.

On Linux systems using systemd or sysvinit, Heartbeat can be run as a service.
Service files and initscripts are provided in the repository in `dist/_lib` and
`dist/_etc` respectively. If you install using the provided ArchLinux package
or a conversion of it to another package manager's format, the systemd service
file will be automatically installed. Currently, no service definitions are
provided for other init systems or operating systems but pull requests are
welcome.

# Developing Plugins
Heartbeat is based around plugins to provide additional services to suit
your needs. Plugins can be producers, subcribers, or both. Heartbeat ships
with a small collection of plugins based on monitoring servers, which you
can use as examples for building your own.

More documentation is provided
[in the Wiki](https://github.com/thenaterhood/heartbeat/wiki/Building-Plugins).

# License
Included software is distributed under the BSD 3-clause license. See LICENSE
for full license text.

If you find Heartbeat useful, please consider contributing, providing feedback
or simply dropping a line to say that Heartbeat was useful to you. If you've
done something cool, let me know!
