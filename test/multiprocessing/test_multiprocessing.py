import unittest
import sys
if (sys.version_info < (3, 3)):
    from mock import MagicMock
    from mock import Mock
else:
    from unittest.mock import MagicMock
    from unittest.mock import Mock
from heartbeat.multiprocessing import Worker
from heartbeat.multiprocessing import LockingDictionary
from queue import Queue


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
