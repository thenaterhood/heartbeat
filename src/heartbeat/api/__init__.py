from enum import Enum


class Signal(object):
    __slots__ = ('sig_type', 'callback')

    def __init__(self, sig_type, callback):
        self.sig_type = sig_type
        self.callback = callback


class SignalType(Enum):
    NEW_EVENT = 'new_event'
    NEW_SYS_EVENT = 'new_sys_event'
    NEW_HUM_EVENT = 'new_hum_event'
    POLL = 'poll'
