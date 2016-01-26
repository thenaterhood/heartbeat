import threading
from time import sleep
from copy import deepcopy


class LockingDictionary(object):

    """
    A thread-safe wrapper for a dictionary with locking
    """
    __slots__ = ('_semaphore', '_dictionary')

    def __init__(self, initial_values=None):
        """
        constructor

        Parameters:
            dict initial_values: Initial values for the dictionary
        """
        if initial_values is None:
            self._dictionary = dict()
        else:
            self._dictionary = initial_values
        self._semaphore = threading.Semaphore()

    def read(self, key):
        """
        Reads a key from the dictionary

        Params:
            mixed key: the key to return the value of
        """
        return self._dictionary[key]

    def write(self, key, value):
        """
        Adds or updates a key in the dictionary

        Params:
            mixed key: the key to add or update
            mixed value: the value to associate with the key
        """
        self._semaphore.acquire()
        self._dictionary[key] = value
        self._semaphore.release()

    def remove(self, key):
        """
        Deletes a key from the dictionary

        Params:
            mixed key: the key to delete
        """
        self._semaphore.acquire()
        del(self._dictionary[key])
        self._semaphore.release()

    def keys(self):
        """
        Returns a list of the dictionary keys
        """
        return self._dictionary.keys()

    def items(self):
        """
        Returns a list of the dictionary items
        """
        return self._dictionary.items()

    def exists(self, key):
        """
        Returns whether a key is in the dictionary
        """
        return (key in self._dictionary)


class Cache(LockingDictionary):

    """
    Handles a persistant cache for storing key-value
    pairs.
    """

    def __init__(self, cache_name, reset=False, settings=None, encryptor=None):
        """
        Parameters:
            str name: The name of the cache
            bool reset: If the cache should be reset if its artifacts already exist
        """
        if settings is None:
            settings = get_config_manager()

        self.directory = settings.heartbeat.cache_dir

        if encryptor is None:
            self.encryptor = Encryptor(settings.heartbeat.secret_key)
        else:
            self.encryptor = encryptor

        super(Cache, self).__init__()
        self.cache_name = cache_name
        if not reset:
            self._load_from_disk()

    def resetValuesTo(self, value):
        """
        Resets all the cache values to a specified value
        """
        self._semaphore.acquire()
        for k in self._dictionary.keys():
            self._dictionary[k] = value
        self._semaphore.release()

    def writeToDisk(self):
        """
        Writes the cache out to disk
        """
        print("Writing cache to disk")
        try:
            with open(self._get_filename(), "wb") as cacheFile:
                data = self.encryptor.encrypt(json.dumps(self._dictionary))
                cacheFile.write(data)
        except Exception as e:
            print(e)

    def _load_from_disk(self):
        """
        Loads the cache from disk
        """
        self._semaphore.acquire()
        try:
            with open(self._get_filename(), "r") as cachefile:
                fcontents = cachefile.read()
                decrypted = self.encryptor.decrypt(fcontents)
                self._dictionary = json.loads(decrypted)
        except Exception as e:
            print(e)
            self._dictionary = {}
        self._semaphore.release()

    def _get_filename(self):
        """
        Generates the filename for the cache
        """
        return os.path.join(
            self.directory,
            sha256(self.cache_name.encode("UTF-8")).hexdigest()
            )


class BackgroundTimer(object):

    """
    A repeating timer that runs in the background
    and calls a provided callback each time the
    timer runs out.
    """

    def __init__(self, interval=60, repeat=True, call=None):
        """
        Parameters:
            int interval: Timer interval, in seconds
            bool repeat: Whether the timer should repeat
            Callable call: A callback to call when the timer hits zero
        """
        self._timer = None
        self.callback = call
        self.interval = interval
        self.repeat = repeat
        self.is_running = False
        if call is None:
            self.callback = do_nothing

    def start(self):
        """
        Starts the timer. This method is safe to call multiple
        times as it will check if the timer is already running.
        If it is, it does nothing, otherwise it starts the timer.
        """
        if not self.is_running:
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def _run(self):
        """
        Private run method. This is called each time the timer
        hits 0.
        """
        self.is_running = False
        if self.repeat:
            self.start()
        self.callback()

    def stop(self):
        """
        Stops and resets the timer.
        """
        self._timer.cancel()
        self.is_running = False

def do_nothing():
    """
    As the name implies, does nothing.
    This is used as the default callback
    for the timer.
    """
    pass
