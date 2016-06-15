# CHANGELOG
_Listed in chronological order (newest is at the bottom of the file)_

0.1
==============

Remove placeholder API key


0.2-1
==============

Fix binary in systemd service file


0.3-5
==============

Fix issues with names and identifying own bcasts


0.4-1
==============

Fix mistake


0.5-1
==============

Fix packaging issues


v0.6.0
==============

Make broadcast push return a status


v1.0.0
==============

Fix populating of source field in Event


v1.0.1
==============

Fix import path


v1.0.2
==============

Fix doxygen configuration


v2.0.0
==============

Bump version numbers, forgot about API-breaking changes


v2.1.0
==============

Bump version numbers for release


v2.2.0
==============

Bump version numbers for release


v2.2.1
==============

Bump version number for release


v2.3.0
==============

Update version number in pkgbuild


v2.3.1
==============

Use new config API where possible


v2.4.0
==============

Fix dependencies and version number


v2.4.1
==============

Bump version number


v2.5.0
==============

Revert back, change is API addition, not breaking


v2.5.1
==============

Fix pkgbuild backup array (remove commas)


v2.5.2
==============

Fix bug in config file detection


v2.6.0
==============

Build
-----------
* setuptools now handles binaries
* Change from pycrypto to pycryptodome

Application
-----------
* Move main method to main package
* Adjustments for move to pycryptodome
* Adjustments to support Windows
* Begin transition to plugin architecture
* Fix silent crash in heartbeat monitoring with bad cache file
* Rename EventType to Topics
* Addition of Timer class for time-based asynchronous tasks
* Change to new module loader
* Misc Improvements in style and naming

_This version of Heartbeat adds experimental support for Windows. Installation requires manual installation of Python and the requirements listed in the setup.py file. It can be run using the startheart command once installed._

_No backwards-incompatible API changes have been made. Previous versions of heartbeat will work with this version and no configuration changes are necessary. Encryption is not supported by versions of Heartbeat prior to 2.5.0._


v2.7.0
==============

Build
-----------
_No changes_

Application
-----------
* Merge NotificationHandler and EventServer
* Update monitor and notification architectures to use plugin architecture
* Add initial support for generic plugins
* Deprecate v2 API methods (see below)

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_The API for writing Notifiers and Monitors is now deprecated in favor of a new plugin architecture. Existing and new plugins should inherit directly from heartbeat.plugin.Plugin and implement the two defined methods documented in that class. Documentation will be forthcoming._


v2.8.0
==============

Build
----------
_no changes_

Application
----------
* Port all plugins to the new architecture (leaving legacy ones in place)
* Repair problems with creating threadpools
* Update and expand tests

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_The API for writing Notifiers and Monitors is now deprecated in favor of a new plugin architecture. Existing and new plugins should inherit directly from heartbeat.plugin.Plugin and implement the two defined methods documented in that class._


v2.9.0
==============

Build
---------
_no changes_

Application
---------
* Update README
* Fix bug in histamine; using variable before setting it
* Remove duplicate notifier load
* Optimizations to heartbeat monitoring plugin
* Fix crash on empty notifier or monitor arrays in config
* Copy Heartbeat functionality to plugin, deprecate builtin module
* Update tests
* Additional deprecation notices

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_The API for writing Notifiers and Monitors is now deprecated in favor of a new plugin architecture. Existing and new plugins should inherit directly from heartbeat.plugin.Plugin and implement the two defined methods documented in that class. Plugins are no longer required to be packaged with Heartbeat. See the Wiki for more details._

_Heartbeat v3.x.x will be released soon, with a number of API-breaking code removals. If you use Heartbeat, port your plugins to the new architecture now._


v2.9.1
==============

Build
---------
_no changes_

Application
---------
* Fix coding errors in pluggable Heartbeat and Pushbullet NotePush

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_The API for writing Notifiers and Monitors is now deprecated in favor of a new plugin architecture. Existing and new plugins should inherit directly from heartbeat.plugin.Plugin and implement the two defined methods documented in that class. Plugins are no longer required to be packaged with Heartbeat. See the Wiki for more details._

_Heartbeat v3.x.x will be released soon, with a number of API-breaking code removals. If you use Heartbeat, port your plugins to the new architecture now._


v2.9.2
==============

Build
--------
_no changes_

Application
--------
* Fix porting errors in pluggables: pushbullet, dweet, histamine

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_The API for writing Notifiers and Monitors is now deprecated in favor of a new plugin architecture. Existing and new plugins should inherit directly from heartbeat.plugin.Plugin and implement the two defined methods documented in that class. Plugins are no longer required to be packaged with Heartbeat. See the Wiki for more details._

_Heartbeat v3.x.x will be released soon, with a number of API-breaking code removals. If you use Heartbeat, port your plugins to the new architecture now._


v2.10.0
==============

Build
--------
_no changes_

Application
--------
* Add error reporting when plugins fail to execute
* Add error reporting when plugins fail to instantiate

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_The API for writing Notifiers and Monitors is now deprecated in favor of a new plugin architecture. Existing and new plugins should inherit directly from heartbeat.plugin.Plugin and implement the two defined methods documented in that class. Plugins are no longer required to be packaged with Heartbeat. See the Wiki for more details._

_Heartbeat v3.x.x will be released soon, with a number of API-breaking code removals. If you use Heartbeat, port your plugins to the new architecture now._


v2.11.0
==============

Build
--------
* Add helper utility to install config and service files
* Remove handling of config and service files from setup.py
* Directory restructuring

Application
--------
* Update a tainted test to reflect new structure


v2.11.1
==============

Build
---------
* Use legacy version of pymlconf for old versions of python. If you're having trouble using Python older than 3.3, uninstall pymlconf then reinstall it through setup.py.

Application
---------
_no changes_

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_The API for writing Notifiers and Monitors is now deprecated in favor of a new plugin architecture. Existing and new plugins should inherit directly from heartbeat.plugin.Plugin and implement the two defined methods documented in that class. Plugins are no longer required to be packaged with Heartbeat. See the Wiki for more details._

_Heartbeat v3.x.x will be released soon, with a number of API-breaking code removals. If you use Heartbeat, port your plugins to the new architecture now._


v3.0.0
==============

Build
--------
* Remove obsolete packages from build process

Application
--------
* Cutover to v3 API
* Removal of deprecated code and settings
* Update tests to match new packages and plugins

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_Many API-breaking changes were introduced in this major release. See the wiki for details on how to transition your setup to V3 (it's easy, I promise)._


v3.1.0
==============

Build
---------
_no changes_

Application
---------
* Add Cache class, with better handling and security
* Migrate heartbeat monitoring to use new cache class

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._


v3.2.0
==============

Build
----------
* Update sample configuration data to include builtin plugin examples

Application
----------
* Add systemd service plugin (heartbeat.pluggable.systemd.Service)

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_No backwards-incompatible API changes have been made. Previous versions of heartbeat will work with this version and no configuration changes are necessary._


v3.2.1
==============

Build
----------
* Fix failing test

Application
----------
_no changes_

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_No backwards-incompatible API changes have been made. Previous versions of heartbeat will work with this version and no configuration changes are necessary._


v3.3.0
==============

Build
------------
_no changes_

Application
------------
* Fix heart monitor plugin immediately marking cached hosts as dead on startup
* Add cache value reset
* Improve thread safety of Cache
* Move plugin activation into PluginRegistry
* Fix heart monitor not iterating correctly on a host flatline
* Cleanup of unneeded imports

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_No backwards-incompatible API changes have been made. Previous versions of heartbeat will work with this version and no configuration changes are necessary._


v3.4.0
==============

Build
--------------
_no changes_

Application
--------------
* Python 3.2 support will be dropped in a future version.
* Add uninstall functionality to install script

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_No backwards-incompatible API changes have been made. Previous versions of heartbeat will work with this version and no configuration changes are necessary._

_Support for Python 3.2 will be dropped in a future version, due to dependencies dropping support as well. Heartbeat may no longer function or install correctly on Python 3.2 after that point._


v3.4.1
==============

Build
-------------
* Don't do python 3.2 warning in setup.py

Application
-------------
* Log and print deprecation warning for python 3.2 on startup

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_No backwards-incompatible API changes have been made. Previous versions of heartbeat will work with this version and no configuration changes are necessary._

__Support for Python 3.2 will be dropped in a future version, due to dependencies dropping support as well. Heartbeat may no longer function or install correctly on Python 3.2 after that point.__


v3.4.2
==============

Build
------------
* Expand tests

Application
------------
* Fix bug in pluggable heartbeat monitor

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_No backwards-incompatible API changes have been made. Previous versions of heartbeat will work with this version and no configuration changes are necessary._

__Support for Python 3.2 will be dropped in a future version, due to dependencies dropping support as well. Heartbeat may no longer function or install correctly on Python 3.2 after that point.__


v3.4.3
==============

Build
-----------
* Expand unit tests for EventServer, MonitorHandler, and PluginRegistry

Application
-----------
* Fix potential issues in retrieving errors from plugins

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_No backwards-incompatible API changes have been made. Previous versions of heartbeat will work with this version and no configuration changes are necessary._

__Support for Python 3.2 will be dropped in a future version, due to dependencies dropping support as well. Heartbeat may no longer function or install correctly on Python 3.2 after that point.__


v3.4.4
==============

Build
-----------
* Adjustment to tests for change in EventServer

Application
-----------
* Fix issue with Event hashes being inconsistent between sessions
* EventServer now remembers past events between sessions (no event spam on start)
* Fix missing imports in multiprocessing module

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_No backwards-incompatible API changes have been made. Previous versions of heartbeat will work with this version and no configuration changes are necessary._

__Support for Python 3.2 will be dropped in the next release. While existing support mechanisms for Python 3.2 will not be removed, Python 3.2 will no longer be tested nor will fixes be provided for it.__


v3.5.0
==============

Build
-----------
* Fix mocking issues in tests

Application
-----------
* Formally drop Python 3.2 support

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_No backwards-incompatible API changes have been made. Previous versions of heartbeat will work with this version and no configuration changes are necessary._

__Support for Python 3.2 has been dropped.__


v3.5.1
==============

Build
-----------
* Add new plugin to same config

Application
-----------
* Add new plugin for startup notifications
* Add new logic for cache paths; use user location if configured one is not writeable
* Update Cache class to use new cache path logic

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_No backwards-incompatible API changes have been made. Previous versions of heartbeat will work with this version and no configuration changes are necessary._


v3.6.0
==============

Build
-----------
_no changes_

Application
-----------
* Add initial support for plugins to declare dependencies on other plugins
* Don't load plugins whose dependencies are not satisfied

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_No backwards-incompatible API changes have been made. Previous versions of heartbeat will work with this version and no configuration changes are necessary. Old versions of heartbeat will not observe dependencies._


v3.7.1
==============

Build
---------
_no changes_

Application
---------
* Formalize API for plugin dependencies
* Fix fatal issues in histamine plugin
* Code style improvements
* Specify exception types, where appropriate
* Clean up unused imports
* Switch to using log format strings, rather than string.format
* Add dyndns dependency on network ip monitors

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_No backwards-incompatible API changes have been made. Previous versions of heartbeat will work with this version and no configuration changes are necessary. Old versions of heartbeat will not observe dependencies._

_Optional methods for plugins have been added; plugins may now depend on services provided by other plugins and advertise their own services. See the Wiki for
more information. These changes will not interfere with plugins operating on prior versions, though prior versions will ignore dependencies._


v3.8.0
==============

Build
---------
_no changes_

Application
---------
* Add event-based heartbeat "Pulse" plugin, as alternative to legacy "Heartbeat"

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_No backwards-incompatible API changes have been made. Previous versions of heartbeat will work with this version and no configuration changes are necessary. Old versions of heartbeat will not observe dependencies._


v3.8.1
==============

Build
----------
* Expand test suite

Application
----------
* Fix minor bug when passing None to get_required_services in Plugin

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_No backwards-incompatible API changes have been made. Previous versions of heartbeat will work with this version and no configuration changes are necessary. Old versions of heartbeat will not observe dependencies._


v3.8.2
==============

Build
----------
* Fix error in tests

Application
----------
_no changes_

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_No backwards-incompatible API changes have been made. Previous versions of heartbeat will work with this version and no configuration changes are necessary. Old versions of heartbeat will not observe dependencies._


v3.9.0
==============

Build
-----------
* Update for new package
* Unit test updates for new package and classes

Application
-----------
* Add dedicated rate limiting class
* Add new topic for startup events
* Fix issues with rate limiting heartbeats and startup events

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_No backwards-incompatible API changes have been made. Previous versions of heartbeat will work with this version and no configuration changes are necessary. Old versions of heartbeat will not observe dependencies. A new event Topic has been added in this version._


v3.9.1
==============

Build
---------
_no changes_

Application
---------
* Fix Heartmonitor pluggable reporting all hosts as flatlined when one flatlines
* Fix Plusemonitor pluggable using duplicate cache name

_Support for Windows is experimental. Installation on Windows using the provided installer requires manual installation of Python and the requirements listed in the setup.py file. Heartbeat can be run from the command line with the 'startheart' command once installed._

_No backwards-incompatible API changes have been made. Previous versions of heartbeat will work with this version and no configuration changes are necessary. Old versions of heartbeat will not observe dependencies. A new event Topic has been added in this version._


v3.9.2
==============

Build
-------------
* Update tests for attribute changes in PluginRegistry

Application
-------------
* PluginRegistry fields now use name mangling
* Addition of get_active_plugins method in PluginRegistry

_No backwards-incompatible API changes have been made. Previous versions of heartbeat will work with this version and no configuration changes are necessary. Old versions of heartbeat will not observe dependencies._


v3.10.0
==============

Build
-------------
* Update package description
* Update PKGBUILD to use tarball instead of zip

Application
-------------
* Added configuration option for querying interval
* Make Events require a title and message on instantiation
* Legacy Heartbeat class now uses logic from Pulse (duplicate code removal)
* Legacy HeartMonitor now uses logic from PulseMonitor (dupe code removal)
* Add configurable selective subscriptions to Histamine modules
* Code style improvements


v3.10.1
==============

Build
------------
* No changes

Application
------------
* Fix repeated instantiation of plugins
* Fix repeated creation of socket listener for heart monitor


v3.10.2
==============

Build
-----------
* No changes

Application
-----------
* Fix requirements issue with HeartMonitor


v3.10.4
==============

Build
-----------
* No changes

Application
-----------
* Fix error in histamine plugin
* Fix error in pulse plugin


v3.11.0
==============

Build
--------------
* No Changes

Application
--------------
* Add signal handling and graceful shutdowns
* Add optional halt() method to Plugin
* Add histamine plugin for local socket to send events to heartbeat (unstable)
* Update service files for proper signaling

v3.12.0
==============

Build
--------------
* No changes

Application
--------------
* Add ACKing support to histamine (and assoc. event types and architecture)
* Misc bugfixes for histamine
* Add changelog
* Fix issue in pushbullet plugin ("too many values")
* Security improvement: Make it harder to spoof event source in histamine
* Use string formatting, not concatonation for log strings

v3.12.1
==============

Build
--------------
* No changes

Application
--------------
* Fix issue with starting plugins twice
