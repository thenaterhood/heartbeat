from queue import Queue
import threading
import logging


class LockingDictionary():

    """
    A thread-safe wrapper for a dictionary with locking
    """
    __slots__ = ('_semaphore', '_dictionary')

    def __init__(self):
        """
        constructor
        """
        self._dictionary = dict()
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
