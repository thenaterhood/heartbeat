"""
Heartbeat plugin for interacting with telegram messenger
This plugin will send messages for events received from heartbeat.

You will need to create a telegram bot and configure its token and provide
a chat ID for it to send messages to.

"""
from telegram.ext import Updater

from heartbeat.network import NetworkInfo
from heartbeat.plugin import Plugin
from heartbeat.platform import Topics, get_config_manager
import urllib.parse
import urllib.request


class Telegram(Plugin):

    """
    Class that sends a single public dweet
    """

    def __init__(self):

        self.config = get_config_manager()
        self._chatid = self.config.notifying.telegram.chat_id
        self._token = self.config.notifying.telegram.token
        self._updater = None

        super(Telegram, self).__init__()

    def get_subscriptions(self):
        """
        Overrides Plugin.get_subscriptions
        """

        subs = {
            Topics.INFO: self._sendmsg,
            Topics.WARNING: self._sendmsg,
            Topics.DEBUG: self._sendmsg,
            Topics.STARTUP: self._sendmsg
            }

        return subs

    def halt(self):
        self.shutdown = True

        if self._updater is not None:
            self._updater.stop()

    def _sendmsg(self, event):
        """
        Sends a telegram message to a telegram group
        """
        msg = "%s: %s from %s" % (event.title, event.message, event.host)

        if self._updater is None:
            self._updater = Updater(token=self._token, use_context=True)

        self._updater.bot.send_message(chat_id=self._chatid, text=msg)

