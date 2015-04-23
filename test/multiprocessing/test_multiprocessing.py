import unittest

from heartbeat.multiprocessing import Worker
from queue import Queue

class WorkerTest(unittest.TestCase):

    def setUp(self):
        self.counter = 0
        self.tasks = 3
        self.queue = Queue(3)
        self.worker = Worker(self.queue)

    def worker_callback(self):
        if (self.counter == self.tasks):
            self.counter += 1
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
        self.worker.start()

        self.assertEqual(self.counter, 1)

    def test_run_twice(self):
        self.tasks = 2
        self.queue.put((self.worker_callback, [], {}))
        self.queue.put((self.worker_callback, [], {}))
        self.worker.start()

        self.assertEqual(self.counter, 2)

    def test_run_thrice(self):
        self.tasks = 3
        self.queue.put((self.worker_callback, [], {}))
        self.queue.put((self.worker_callback, [], {}))
        self.queue.put((self.worker_callback, [], {}))
        self.worker.start()

        self.assertEqual(self.counter, 3)



