from blinkstick import blinkstick
from heartbeat.notifications import Notifier
from heartbeat.platform import get_config_manager, Topics
from datetime import datetime


class BlinkStickColor(Notifier):

    __slots__ = ('message', 'title', 'serial', 'warning', 'okay',
                 'alert', 'use_color', 'previous_warnings')

    def __init__(self):
        print("Initting blinkstick module")
        config = get_config_manager()
        self.previous_warnings = {}
        self.serial = config.notifying.blinkstick.serial
        self.warning = config.notifying.blinkstick.warning_color
        self.okay = config.notifying.blinkstick.okay_color
        self.alert = config.notifying.blinkstick.alert_color
        self.use_color = self.okay

        super(BlinkStickColor, self).__init__()
        self.run()

    def _choose_color(self, event):
        if (event.type == Topics.WARNING):
            self.use_color = self.alert
            self.previous_warnings[event.source] = event.timestamp

        elif (event.type == Topics.INFO):
            if (event.source in self.previous_warnings):
                del(self.previous_warnings[event.source])

            if (len(self.previous_warnings) < 1):
                self.use_color = self.okay

        else:
            self.use_color = self.okay

        print("Using color " + self.use_color)

    def load(self, event):
        host = event.host
        self.title = event.title + ": " + host
        date = datetime.now()
        self.message = host + ": " + event.message + " at " + \
            event.timestamp.strftime("%H:%M:%S %m/%d/%y")

        self._choose_color(event)

    def run(self):
        bstick = blinkstick.find_by_serial(self.serial)
        if (bstick == None):
            print("Blinkstick not found")
        else:
            bstick.set_color(hex=self.use_color)
