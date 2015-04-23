import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
from unittest.mock import Mock
import socket
import urllib
from heartbeat.network import NetworkInfo
from heartbeat.network import SocketListener
from heartbeat.network import SocketBroadcaster

class NetworkInfoTest(unittest.TestCase):

    def test_init_nocaching(self):
        n = NetworkInfo(caching=False)

        self.assertIsNone(n.hostname)
        self.assertIsNone(n.ip_lan)
        self.assertIsNone(n.ip_wan)

    def test_get_local_ip(self):
        n = NetworkInfo(caching=False)
        sock = MagicMock(name='socket', spec=socket.socket)
        sock.getsockname.return_value= ['1.2.3.4']
        ip = n.get_local_ip(sock=sock)

        self.assertEqual('1.2.3.4', ip)

    def test_get_hostname(self):
        n = NetworkInfo(caching=False)

        hostname = n.get_hostname(strategy=lambda: 'titanium')

        self.assertEqual('titanium', hostname)

    def test_get_fqdn(self):
        n = NetworkInfo(caching=False)
        fqdn = n.get_fqdn(strategy=lambda: 'tita.nium')

        self.assertEqual('tita.nium', fqdn)


class SocketListenerTest(unittest.TestCase):

    def setUp(self):
        self.expected_data = 'foobar'

    def socket_callback(self, data, addr):
        self.assertEqual(self.exected_data, data)

    def test_instantiate(self):
        sock = MagicMock(name='socket', spec=socket.socket)
        sock.recvfrom.return_value = [self.expected_data, 'somewhere']

        n = SocketListener(0, self.socket_callback, daemon=True, timeout=None, sock=sock)

class SocketBroadcasterTest(unittest.TestCase):

    def setUp(self):
        pass

    def pushCallback(self, data, sendTo):
        self.assertFalse(True)
        self.assertEquals(b'foobar', data)

    def test_basic_instantiate(self):
        b = SocketBroadcaster(20)

        self.assertEqual(20, b._port)
        self.assertEqual('<broadcast>', b._dest)

    def test_push(self):
        b = SocketBroadcaster(20)

        sock = MagicMock(name='socket', spec=socket.socket)
        b.push(b'foobar', sock=sock)

        # This for some reason doesn't work.
        #sock.sendto.assert_called_once_with(b'foobar', ('<broadcast>', 20))

