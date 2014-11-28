import threading


class MonitorWorker(threading.Thread):

    def __init__(self, callback):
        """
        Constructor

        Params:
            Function callback: A method to call when the MonitorWorker
                discovers something of note, or just feels lonely
        """
        self.callback = callback
        super(MonitorWorker, self).__init__()

    def run(self):
        """
        Runs the thing. Usually called from the parent start()
        """
        raise NotImplementedError("This method is not implemented.")
