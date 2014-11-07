import select
import socket
import threading
from queue import Queue, Empty

class NetworkInfo():
    """
    Contains network data
    """

    def __init__(self):
        """
        Constructor
        """
        self.ip_lan = self.get_local_ip()
        self.hostname = socket.gethostname()
        self.fqdn = socket.getfqdn()

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout( 5 )
        try:
            s.connect(("google.com",80))
            ip = s.getsockname()[0]
            s.close()
        except:
            ip = "0.0.0.0"

        return ip

class SocketListener(threading.Thread):
    """
    Listens on a socket and calls back when
    data is received.

    Extends threading.Thread
    """

    def __init__(self, port, callback, daemon = True):
        """
        Constructor

        Parameters:
            int      port:     The port to listen to
            Function callback: The function to call when data is received
            bool     daemon:   Whether to run as a daemon thread
        """
        self.port = port
        self.callback = callback

        listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen.bind(('', self.port))
        self.listen_socket = listen
        super().__init__(daemon = daemon)

    def _listen(self):
        """
        Listens for data then calls back when data is received
        """
        data, addr = self.listen_socket.recvfrom(1024)
        self.callback(data, addr)

    def run(self):
        """
        Runs the thread (typically with the Thread start() method)
        """
        while True:
            self._listen()

class SocketBroadcaster():
    """
    Sends a broadcast packet containing data on a given port
    """

    __slots__ = ('_bcast_socket', '_port')

    def __init__(self, port):
        """
        Constructor

        Params:
            int port: The port to broadcast on
        """
        bcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bcast.bind(('', 0))
        bcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._port = port
        self._bcast_socket = bcast

    def push(self, data):
        """
        Sends a broadcast

        Params:
            binary data: Encoded data to send
        """
        self._bcast_socket.sendto(data, ('<broadcast>', self._port))

if __name__ == '__main__':
    netinfo = NetworkInfo()
    print(netinfo.ip_lan)
