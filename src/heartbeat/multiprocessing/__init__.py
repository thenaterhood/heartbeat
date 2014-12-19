from queue import Queue
import threading


class Worker(threading.Thread):

    """
    Worker thread for executing threadpool tasks
    """

    def __init__(self, tasks):
        """
        Constructor

        Parameters:
            Queue tasks: a queue of tasks for the worker to access
        """
        super(Worker, self).__init__()

        self.shutdown = False
        self.tasks = tasks
        self.daemon = True

    def run(self):
        """
        Run method for the worker, called via start
        """
        while not self.shutdown:
            call, args, kwargs = self.tasks.get()
            try:
                call(*args, **kwargs)
            except Exception:
                print(e)

            self.tasks.task_done()

class Threadpool:

    """
    Threadpool handling tasks from a queue
    """

    def __init__(self, threads):
        """
        Constructor

        Parameters:
            int threads: the number of threads for the pool to use
        """
        self.workers = []
        self.tasks = Queue(threads)

        for n in range(0, threads):
            w = Worker(self.tasks)
            w.start()
            self.workers.append(w)

    def add(self, call, *args, **kwargs):
        """
        Add a task to the queue

        Parameters:
            Function call: function to call
            list args: Arguments for the function
            list kwargs: keyword arguments for the function
        """
        self.tasks.put((call, args, kwargs))

    def terminate(self):
        """
        Immediately shuts down the threadpool by telling all the
        worker threads to stop after completing their current task
        """
        for w in self.workers:
            w.shutdown = True
            w.join()

    def join(self):
        """
        Joins the threadpool and waits for it to complete
        """
        self.tasks.join()

