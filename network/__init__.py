import select
import socket
import threading
from queue import Queue, Empty

def get_local_ip():
        def udp_listening_server():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind(('<broadcast>', 8888))
            s.setblocking(0)
            while True:
                result = select.select([s],[],[])
                msg, address = result[0][0].recvfrom(1024)
                msg = str(msg, 'UTF-8')
                if msg == 'What is my LAN IP address?':
                    break
            queue.put(address)

        queue = Queue()
        thread = threading.Thread(target=udp_listening_server)
        thread.queue = queue
        thread.start()
        s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s2.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        waiting = True
        while waiting:
            s2.sendto(bytes('What is my LAN IP address?', 'UTF-8'), ('<broadcast>', 8888))
            try:
                address = queue.get(False)
            except Empty:
                pass
            else:
                waiting = False
        return address[0]

class NetworkInfo():
    def __init__(self):
        self.ip_lan = get_local_ip()
        self.hostname = socket.gethostname()
        self.fqdn = socket.getfqdn()

class SocketListener(threading.Thread):

    def __init__(self, port, callback):
        self.port = port
        self.callback = callback

        listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen.bind(('', self.port))
        self.listen_socket = listen
        super().__init__(daemon = True)

    def _listen(self):
        data, addr = self.listen_socket.recvfrom(1024)
        self.callback(data, addr)

    def run(self):
        while True:
            self._listen()

class SocketBroadcaster():

    __slots__ = ('_bcast_socket', '_port')

    def __init__(self, port):
        bcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bcast.bind(('', 0))
        bcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._port = port
        self._bcast_socket = bcast

    def push(self, data):
        self._bcast_socket.sendto(data, ('<broadcast>', self._port))

if __name__ == '__main__':
    print(get_local_ip())
