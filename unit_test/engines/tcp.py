import socket

class engine_tcp(object):
    def __init__(self, host, port):
        self.uid = None
        self.host = host
        self.port = port
        self.buffer = ''
        self.socket = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error, msg:
            sys.stderr.write("[!] %s\n" % msg[1])
            return False
        try:
            self.sock.connect((self.host, self.port))
        except socket.error, msg:
            sys.stderr.write("[!] %s\n" % msg[1])
            return False
        return True

    def send(self, json):
        if self.uid is not None:
            json = json.replace('$uid', self.uid)
        return self.sock.send("\x00" + json + "\n\xff")

    def receive(self):
        self.buffer = self.sock.recv(8096)
        return self.buffer[1:-1]

    def disconnect(self):
        self.sock.close()
        return True
