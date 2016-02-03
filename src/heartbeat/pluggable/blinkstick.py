"""
Heartbeat plugin that manipulates blinksticks

Colors and blinkstick selection can be set in the
heartbeat notifiers.conf file (/etc/heartbeat/notifying.conf)
in most unix-based systems.

A sample configuration section in that file for this plugin
is as follows:

blinkstick:
    serial: YOUR_BLINKSTICK_SERIAL
    warning_color: "#ff0000"
    okay_color: "#00ff00"
    alert_color: "ffff00"
"""


from blinkstick import blinkstick
from heartbeat.platform import get_config_manager, Topics
from heartbeat.plugin import Plugin


class Color(Plugin):

    """
    Changes the color of a blinkstick based on Events
    """

    __slots__ = ('message', 'title', 'serial', 'warning', 'okay',
                 'alert', 'previous_warnings')

    def __init__(self):
        print("Initting blinkstick module")
        config = get_config_manager()
        self.previous_warnings = {}
        self.serial = config.notifying.blinkstick.serial
        self.warning = config.notifying.blinkstick.warning_color
        self.okay = config.notifying.blinkstick.okay_color
        self.alert = config.notifying.blinkstick.alert_color

        super(Color, self).__init__()

    def get_subscriptions(self):
        """
        @override: Plugin.get_subscriptions

        """

        subs = {
                Topics.INFO: self.info_callback,
                Topics.WARNING: self.warning_callback,
                }

        return subs

    def info_callback(self, event):
        """
        The callback method for an informational event
        """

        if event.source in self.previous_warnings:
            del(self.previous_warnings[event.source])

        self._select_color()

    def warning_callback(self, event):
        """
        The callback method for a warning event
        """

        self.previous_warnings[event.source] = event.timestamp

        self._select_color()

    def _select_color(self):
        """
        Selects the color to set the blinkstick to
        """

        if len(self.previous_warnings) < 1:
            self._set_color(self.okay)

        elif len(self.previous_warnings) > 0:
            self._set_color(self.alert)

    def _set_color(self, color):
        """
        Sets the actual blinkstick color
        """

        bstick = blinkstick.find_by_serial(self.serial)
        if (bstick == None):
            pass
        else:
            bstick.set_color(hex=color)
