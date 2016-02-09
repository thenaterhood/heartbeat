import unittest
import sys
if (sys.version_info < (3, 3)):
    from mock import MagicMock
    from mock import Mock
    from mock import ANY
else:
    from unittest.mock import MagicMock
    from unittest.mock import Mock
    from unittest.mock import ANY

from heartbeat.pluggable.heartbeat import Heartbeat, Monitor
from heartbeat.pluggable.heartbeat import Pulse, PulseMonitor
from heartbeat.network import SocketBroadcaster, SocketListener, NetworkInfo
from heartbeat.platform import Event, Topics
from heartbeat.monitoring import MonitorHandler, MonitorType
from heartbeat.multiprocessing import Cache, BackgroundTimer
from pymlconf import ConfigManager

import datetime
from time import time

import concurrent.futures

class TestHeartbeat(unittest.TestCase):

    def setUp(self):
        interval = 2
        secret = 'heartbeat'
        self.bcaster = Mock(name='bcaster', spec=SocketBroadcaster)
        self.settings = Mock(name='settings', spec=ConfigManager)
        self.settings.heartbeat = Mock(name='hbnamespace', spec=ConfigManager)
        self.settings.heartbeat.secret_key = 'heartbeat3477'
        self.bcaster.push = MagicMock(return_value=None)
        self.hb = Heartbeat(self.bcaster, None, self.settings)

    def test_instantiate(self):
        interval = 2
        secret = 'heartbeat'
        bcaster = Mock(name='bcaster', spec=SocketBroadcaster)
        hb = Heartbeat(bcaster, None, self.settings)

        self.assertEqual(b'heartbeat3477', hb.secret)
        self.assertEqual(bcaster, hb.bcaster)

    def test_beat(self):
        self.hb._beat()

        self.hb.bcaster.push.assert_called_once_with(ANY)


class TestPulse(unittest.TestCase):

    def setUp(self):
        self.timer = Mock(name='timer', spec=BackgroundTimer)
        self.netinfo = Mock(name='network', spec=NetworkInfo)
        self.hb = Pulse(self.timer, self.netinfo)

    def test_instantiate(self):
        hb = Pulse(self.timer, self.netinfo)

    def test_beat(self):
        func = MagicMock(return_value=None)
        self.hb.callback = func
        self.hb._beat()

        func.assert_called_once_with(ANY)


class TestMonitor(unittest.TestCase):

    def setUp(self):
        self.cache = Mock(name='cache', spec=Cache)
        self.listener = Mock(name='listener', spec=SocketListener)
        self.settings = Mock(name='settings', spec=ConfigManager)
        self.settings.heartbeat = Mock(name='settings', spec=ConfigManager)
        self.settings.heartbeat.port = '8080'
        self.settings.heartbeat.secret_key = 'heartbeat3477'
        self.monitor = Monitor(
                cache=self.cache,
                settings=self.settings,
                listener=self.listener
                )

    def test_init(self):
        monitor = Monitor(
                cache=self.cache,
                settings=self.settings,
                listener=self.listener
                )

        self.assertEqual(self.listener, monitor.listener)
        self.assertEqual(self.settings.heartbeat.port, monitor.port)
        self.assertEqual(self.cache, monitor.cache)

    def test_get_producers(self):
        prods = self.monitor.get_producers()
        correct = {
                MonitorType.REALTIME: self.monitor.run,
                MonitorType.PERIODIC: self.monitor.cleanup_hosts
                }

        self.assertEqual(correct, prods)

    def test__log_host(self):

        self.monitor.cache.write = MagicMock(return_value=None)
        self.monitor.cache.keys = MagicMock(return_value=[])
        self.monitor.callback = MagicMock()

        self.monitor._log_host('foo.example.com')
        self.monitor.cache.write.assert_called_with('foo.example.com', ANY)
        self.monitor.callback.assert_called_with(ANY)

        self.monitor._log_host('foo.example.com')
        self.monitor.cache.write.assert_called_with('foo.example.com', ANY)

    def test_cleanup_hosts(self):

        self.monitor.cache.write = MagicMock(return_value=None)
        self.monitor.cache.keys = MagicMock(return_value=['foo.example.com'])
        self.monitor.cache.items = MagicMock(return_value=[('foo.example.com', 1453848040.6469207)])
        self.monitor.callback = MagicMock()
        self.monitor.cache.read = MagicMock(return_value=datetime.datetime(year=1970, month=1, day=1))

        cb = MagicMock(return_value=None)
        self.monitor.cleanup_hosts(cb)
        cb.assert_called_once_with(ANY)

    def test_cleanup_hosts_no_expired(self):
        self.monitor.cache.write = MagicMock(return_value=None)
        self.monitor.cache.keys = MagicMock(return_value=['foo.example.com'])
        self.monitor.cache.items = MagicMock(return_value=[('foo.example.com', time())])
        self.monitor.callback = MagicMock()
        self.monitor.cache.read = MagicMock(return_value=datetime.datetime(year=1970, month=1, day=1))

        cb = MagicMock(return_value=None)
        self.monitor.cleanup_hosts(cb)


class TestPulseMonitor(unittest.TestCase):

    def setUp(self):
        self.cache = Mock(name='cache', spec=Cache)
        self.monitor = PulseMonitor(
                cache=self.cache,
                )

    def test_init(self):
        monitor = PulseMonitor(
                cache=self.cache,
                )

        self.assertEqual(self.cache, monitor.cache)

    def test_get_producers(self):
        prods = self.monitor.get_producers()
        correct = {
                MonitorType.PERIODIC: self.monitor.cleanup_hosts
                }

        self.assertEqual(correct, prods)

    def test_get_subscriptions(self):
        subs = self.monitor.get_subscriptions()
        correct = {
                Topics.HEARTBEAT: self.monitor.receive
                }

        self.assertEqual(correct, subs)

    def test__log_host(self):

        self.monitor.cache.write = MagicMock(return_value=None)
        self.monitor.cache.keys = MagicMock(return_value=[])
        self.monitor.callback = MagicMock()

        self.monitor._log_host('foo.example.com')
        self.monitor.cache.write.assert_called_with('foo.example.com', ANY)
        self.monitor.callback.assert_called_with(ANY)

        self.monitor._log_host('foo.example.com')
        self.monitor.cache.write.assert_called_with('foo.example.com', ANY)

    def test_cleanup_hosts(self):

        self.monitor.cache.write = MagicMock(return_value=None)
        self.monitor.cache.keys = MagicMock(return_value=['foo.example.com'])
        self.monitor.cache.items = MagicMock(return_value=[('foo.example.com', 1453848040.6469207)])
        self.monitor.callback = MagicMock()
        self.monitor.cache.read = MagicMock(return_value=datetime.datetime(year=1970, month=1, day=1))

        cb = MagicMock(return_value=None)
        self.monitor.cleanup_hosts(cb)
        cb.assert_called_once_with(ANY)

    def test_cleanup_hosts_no_expired(self):
        self.monitor.cache.write = MagicMock(return_value=None)
        self.monitor.cache.keys = MagicMock(return_value=['foo.example.com'])
        self.monitor.cache.items = MagicMock(return_value=[('foo.example.com', time())])
        self.monitor.callback = MagicMock()
        self.monitor.cache.read = MagicMock(return_value=datetime.datetime(year=1970, month=1, day=1))

        cb = MagicMock(return_value=None)
        self.monitor.cleanup_hosts(cb)


