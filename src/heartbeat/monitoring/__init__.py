

class Monitor():

    def __init__(self, callback):
        """
        Constructor

        Params:
            Function callback: A method to call when the MonitorWorker
                discovers something of note, or just feels lonely
        """
        self.callback = callback
        self.realtime = False
        self.shutdown = False

    def run(self):
        """
        Runs the thing. Usually called from the parent start()
        """
        raise NotImplementedError("This method is not implemented.")
