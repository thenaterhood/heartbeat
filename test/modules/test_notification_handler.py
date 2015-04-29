import unittest
import sys
if (sys.version_info < (3, 3)):
    from mock import MagicMock
    from mock import Mock
else:
    from unittest.mock import MagicMock
    from unittest.mock import Mock

from heartbeat.modules import Heartbeat
from heartbeat.network import SocketBroadcaster
from heartbeat.modules import NotificationHandler
from heartbeat.modules import MonitorHandler
from heartbeat.monitoring import Monitor
from heartbeat.notifications import Notifier
from heartbeat.platform import Event

import concurrent.futures
import datetime


class TestNotificationHandler(unittest.TestCase):

    def setUp(self):
        pool = MagicMock(name="threadpool", spec=concurrent.futures.ThreadPoolExecutor)

        self.notifiers = []
        self.notifiers.append(Mock(name="n1", spec=Notifier))
        self.notifiers.append(Mock(name="n2", spec=Notifier))

        self.notification_handler = NotificationHandler(
                self.notifiers,
                pool
                )

    def test_receive_event(self):
        e = Event()

        self.notification_handler.receive_event(e)

        self.notification_handler.threadpool.submit.assert_called_with(self.notifiers[1]().run)

    def test_event_delay_passed(self):
        e = Event()

        self.notification_handler.eventTime.write(e.__hash__(), e.timestamp)
        self.assertFalse(self.notification_handler.event_delay_passed(e))

        delta = datetime.timedelta(hours=2)
        hours_ago = e.timestamp - delta
        self.notification_handler.eventTime.write(e.__hash__(), hours_ago)
        self.assertTrue(self.notification_handler.event_delay_passed(e))
