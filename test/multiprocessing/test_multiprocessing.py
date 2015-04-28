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

class WorkerTest(unittest.TestCase):

    def setUp(self):
        with open('derp.log', 'a') as derp:
            derp.write("Starting a new test\n")
        self.counter = 0
        self.exception_counter = 0
        self.tasks = 3
        self.queue = Queue(3)
        self.worker = Worker(self.queue)

    def worker_exception_callback(self, e):
        self.exception_counter = 1
        self.worker.shutdown = True
        self.queue.put((self.worker_callback, [], {}))

    def worker_callback_raise_exception(self):
        raise Exception("Testing")

    def worker_callback(self):
        if (self.counter >= self.tasks):
            self.worker.shutdown = True
            self.queue.put((self.worker_callback, [], {}))
        else:
            self.counter += 1

    def test_basic_instantiate(self):
        w = Worker(self.queue)

        self.assertEqual(w.shutdown, False)
        self.assertEqual(w.tasks, self.queue)
        self.assertEqual(w.daemon, True)
        self.assertEqual(w.exception_func, None)

    def test_run_once(self):
        self.tasks = 1
        self.queue.put((self.worker_callback, [], {}))
        self.worker.run()

        self.assertEqual(self.counter, 1)

    def test_run_twice(self):
        self.tasks = 2
        self.queue.put((self.worker_callback, [], {}))
        self.queue.put((self.worker_callback, [], {}))
        self.worker.run()

        self.assertEqual(self.counter, 2)

    def test_run_thrice(self):
        self.tasks = 3
        self.queue.put((self.worker_callback, [], {}))
        self.queue.put((self.worker_callback, [], {}))
        self.queue.put((self.worker_callback, [], {}))
        self.worker.run()

        self.assertEqual(self.counter, 3)

    def test_exception_callback(self):
        self.tasks = 1
        self.queue.put((self.worker_callback_raise_exception, [], {}))
        self.worker.exception_func = self.worker_exception_callback
        self.worker.run()

        self.assertEqual(self.exception_counter, 1)

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
