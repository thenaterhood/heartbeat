import unittest
import sys
if (sys.version_info < (3, 3)):
    from mock import MagicMock
    from mock import Mock
    from mock import mock_open
    from mock import patch
else:
    from unittest.mock import MagicMock
    from unittest.mock import Mock
    from unittest.mock import mock_open
    from unittest.mock import patch
from heartbeat.multiprocessing import LockingDictionary, Cache
from heartbeat.security import Encryptor
from pymlconf import ConfigManager
from queue import Queue

patch('__main__.open', mock_open)


class LockingDictionaryTest(unittest.TestCase):

    def setUp(self):
        self.ld = LockingDictionary()

    def test_write(self):
        self.ld.write('foo', 'bar')

        self.assertTrue('foo' in self.ld._dictionary)
        self.assertEqual('bar', self.ld._dictionary['foo'])

    def test_read(self):
        self.ld.write('foo', 'bar')

        self.assertEqual('bar', self.ld.read('foo'))

    def test_remove(self):
        self.ld.write('foo', 'bar')
        self.ld.remove('foo')

        self.assertFalse('foo' in self.ld._dictionary)

    def test_keys(self):
        self.ld.write('foo', None)
        self.ld.write('bar', None)

        self.assertTrue('foo' in self.ld.keys())
        self.assertTrue('bar' in self.ld.keys())

    def test_items(self):
        self.ld.write('foo', 'bar')
        self.ld.write('heart', 'beat')

        self.assertTrue(('foo', 'bar') in self.ld.items())
        self.assertTrue(('heart', 'beat') in self.ld.items())

    def test_exists(self):
        self.ld.write('foo', 'bar')
        self.ld.write('heart', 'beat')

        self.assertTrue(self.ld.exists('foo'))
        self.assertTrue(self.ld.exists('heart'))

class TestCache(unittest.TestCase):

    """
    This is minimal, since most class methods are
    inherited from LockingDictionary which has
    a complete test suite already
    """

    def setUp(self):
        self.settings = Mock(name="settings", spec=ConfigManager)
        self.settings.heartbeat = Mock(name="hbnamespace", spec=ConfigManager)
        self.settings.heartbeat.secret_key = "heartbeat3477"
        self.settings.heartbeat.cache_dir = "/foo"
        self.encryptor = Mock(name='enc', spec=Encryptor)
        self.c = Cache('test-cache', False, self.settings, self.encryptor)

    def test_init(self):
        c = Cache('test-cache-init', False, self.settings, self.encryptor)

        self.assertEqual(c.encryptor, self.encryptor)
        self.assertEqual(c.cache_name, 'test-cache-init')

    def test_resetValuesTo(self):
        self.c.write("key", "value")
        self.c.write("foo", "bar")

        self.c.resetValuesTo('nada')

        self.assertEqual('nada', self.c.read('key'))
        self.assertEqual('nada', self.c.read('foo'))

