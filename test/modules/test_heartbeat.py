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

from heartbeat.modules import Heartbeat
from heartbeat.network import SocketBroadcaster
from heartbeat.modules import EventServer
from heartbeat.monitoring import MonitorHandler
from heartbeat.monitoring import Monitor

import concurrent.futures

class TestHeartbeat(unittest.TestCase):

    def setUp(self):
        interval = 2
        secret = 'heartbeat'
        self.bcaster = Mock(name='bcaster', spec=SocketBroadcaster)
        self.bcaster.push = MagicMock(return_value=None)
        self.hb = Heartbeat(interval, secret, self.bcaster)

    def test_instantiate(self):
        interval = 2
        secret = 'heartbeat'
        bcaster = Mock(name='bcaster', spec=SocketBroadcaster)
        hb = Heartbeat(interval, secret, bcaster)

        self.assertEqual(2, hb.interval)
        self.assertEqual(b'heartbeat', hb.secret)
        self.assertEqual(bcaster, hb.bcaster)

    def test_beat(self):
        self.hb._beat()

        self.hb.bcaster.push.assert_called_once_with(ANY)
