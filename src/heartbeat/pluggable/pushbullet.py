"""
Heartbeat plugin for interacting with Pushbullet.
Many of these plugins support interacting with
multiple Pushbullet accounts.

This plugin can be configured by adding the following
section to /etc/heartbeat/notifying.conf (or the corresponding
location for your install):

pushbullet:
    api_keys:
        - YOUR_FIRST_API_KEY
        - YOUR_SECOND_API_KEY
"""

from pushbullet import PushBullet
from heartbeat.plugin import Plugin
from heartbeat.platform import get_config_manager, Topics


class NotePush(Plugin):

    """
    Makes a note push to Pushbullet
    """

    __slots__ = ('api_keys')

    def __init__(self):
        config = get_config_manager()
        self.api_keys = config.notifying.pushbullet.api_keys
        super(NotePush, self).__init__()

    def get_subscriptions(self):
        """
        Overrides Plugin.get_subscriptions
        """

        subs = {
            Topics.INFO: self.push_note,
            Topics.WARNING: self.push_note,
            Topics.STARTUP: self.push_note
            }

        return subs

    def push_note(self, event):
        """
        Pushes a note to the configured pushbullet accounts
        """

        host = event.host
        title = event.title + ": " + host
        message = host + ": " + event.message + " at " + \
                event.timestamp.strftime("%H:%M:%S %m/%d/%y")

        for key in self.api_keys:
            pb = PushBullet(key)
            success, push = pb.push_note(title, message)
