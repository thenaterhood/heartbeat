import select
import socket
import threading
import urllib.request
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
        self.ip_wan = self.get_public_ip()
        self.hostname = socket.gethostname()
        self.fqdn = socket.getfqdn()

    def get_local_ip(self):
        """
        Grabs the local IP of the system

        Returns:
            string ip: the ip address
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(5)
        try:
            s.connect(("google.com", 80))
            ip = s.getsockname()[0]
            s.close()
        except:
            ip = "0.0.0.0"

        return ip

    def get_public_ip(self):
        """
        Grabs the public IP of the network

        Returns:
            string ip: the public ip address
        """
        try:
            filehandle = urllib.request.urlopen(
                'http://icanhazip.com', timeout=5)
            ip = filehandle.readlines()[0].decode('UTF-8').strip()
        except:
            ip = '0.0.0.0'

        return ip


class SocketListener(threading.Thread):

    """
    Listens on a socket and calls back when
    data is received.

    Extends threading.Thread
    """

    def __init__(self, port, callback, daemon=True, timeout=None):
        """
        Constructor

        Parameters:
            int      port:     The port to listen to
            Function callback: The function to call when data is received
            bool     daemon:   Whether to run as a daemon thread
        """
        super(SocketListener, self).__init__()
        self.daemon = daemon
        self.port = port
        self.callback = callback

        listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if (timeout is not None):
            listen.settimeout(timeout)

        listen.bind(('', self.port))
        self.listen_socket = listen
        self.shutdown = False

    def _listen(self):
        """
        Listens for data then calls back when data is received
        """
        try:
            data, addr = self.listen_socket.recvfrom(1024)
            self.callback(data, addr)
        except socket.timeout:
            pass

    def run(self):
        """
        Runs the thread (typically with the Thread start() method)
        """
        while not self.shutdown:
            self._listen()


class SocketBroadcaster():

    """
    Sends a broadcast packet containing data on a given port
    """

    __slots__ = ('_bcast_socket', '_port', '_dest')

    def __init__(self, port, dest='<broadcast>'):
        """
        Constructor

        Params:
            int port: The port to broadcast on
        """
        self._port = port

        if (dest is None):
            dest = '<broadcast>'

        self._dest = dest

    def push(self, data):
        """
        Sends a broadcast

        Params:
            binary data: Encoded data to send
        Returns:
            boolean: true on success, false on failure
        """
        success = False
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if (self._dest == '<broadcast>'):
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        try:
            sock.sendto(data, (self._dest, self._port))
            success = True
            sock.shutdown(1)
        except:
            pass
        sock.close()
        return success

if __name__ == '__main__':
    netinfo = NetworkInfo()
    print("Network info for the local system:")
    print("Local IP address (if determinable): " + netinfo.ip_lan)
    print("Local fqdn: " + netinfo.fqdn)
    print("Local hostname: " + netinfo.hostname)
