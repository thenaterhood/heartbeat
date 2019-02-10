

class EventRegistry(type):
    """
    @since v3.13.0
    """

    __buffer_end = 50
    __buffer = [None] * (__buffer_end)
    __buffer_pointer = 0

    def __init__(cls, name, bases, attrs):

        EventRegistry.__set_buffer_next(cls)

    def __get_buffer_latest():

        latest_index = EventRegistry.__buffer_pointer - 1
        if latest_index < 0:
            latest_index = EventRegistry.__buffer_end

        return EventRegistry.__buffer[latest_index]

    def __set_buffer_next(value):

        EventRegistry.__buffer[EventRegistry.buffer_pointer] = value

        EventRegistry.__buffer_pointer += 1
        if (EventRegistry.__buffer_pointer > EventRegistry.__buffer_end):
            EventRegistry.__buffer_pointer = 0
