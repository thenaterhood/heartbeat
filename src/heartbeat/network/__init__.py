import socket
import threading
import urllib.request


class NetworkInfo(object):

    """
    Contains network data
    """

    def __init__(self, caching=True):
        """
        Constructor
        """
        if (caching):
            self.ip_lan = self.get_local_ip()
            self.ip_wan = self.get_public_ip()
            self.hostname = self.get_hostname()
            self.fqdn = self.get_fqdn()
        else:
            self.ip_lan = None
            self.ip_wan = None
            self.hostname = None
            self.fqdn = None

    def get_local_addresses(self):
        wan_ip = self.ip_wan if self.ip_wan is not None else self.get_public_ip()
        hostname = self.hostname if self.hostname is not None else self.get_hostname()
        lan_ip = self.ip_lan if self.ip_lan is not None else self.get_local_ip()

        return [
                hostname,
                self.get_fqdn() if self.fqdn is None else self.fqdn,
                lan_ip,
                wan_ip,
                wan_ip + "-" + hostname,
                lan_ip + "-" + hostname,
                "localhost",
                "127.0.0.1"
                ]

    def get_hostname(self, strategy=socket.gethostname):
        return strategy()

    def get_fqdn(self, strategy=socket.getfqdn):
        return strategy()

    def get_local_ip(self, sock=None):
        """
        Grabs the local IP of the system

        Returns:
            string ip: the ip address
        """
        if sock is None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        sock.settimeout(5)
        try:
            sock.connect(("google.com", 80))
            ip = sock.getsockname()[0]
            sock.close()
        except Exception:
            ip = "0.0.0.0"

        return ip

    def get_public_ip(self, url_lib=urllib):
        """
        Grabs the public IP of the network

        Returns:
            string ip: the public ip address
        """
        try:
            filehandle = url_lib.request.urlopen(
                'http://icanhazip.com', timeout=5)
            ip = filehandle.readlines()[0].decode('UTF-8').strip()
        except Exception:
            ip = '0.0.0.0'

        return ip


class SocketListener(threading.Thread):

    """
    Listens on a socket and calls back when
    data is received.

    Extends threading.Thread
    """

    def __init__(self, port, callback, daemon=True, timeout=None, sock=socket.socket):
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

        listen = sock(socket.AF_INET, socket.SOCK_DGRAM)
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


class SocketBroadcaster(object):

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

    def push(self, data, sock=socket.socket):
        """
        Sends a broadcast

        Params:
            binary data: Encoded data to send
        Returns:
            boolean: true on success, false on failure
        """
        success = False
        pusher = sock(socket.AF_INET, socket.SOCK_DGRAM)

        if (self._dest == '<broadcast>'):
            pusher.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        try:
            pusher.sendto(data, (self._dest, self._port))
            success = True
            pusher.shutdown(1)
        except Exception:
            pass

        pusher.close()
        return success

if __name__ == '__main__':
    netinfo = NetworkInfo()
    print("Network info for the local system:")
    print("Local IP address (if determinable): " + netinfo.ip_lan)
    print("Local fqdn: " + netinfo.fqdn)
    print("Local hostname: " + netinfo.hostname)
    print("WAN IP address (if determinable): " + netinfo.ip_wan)
