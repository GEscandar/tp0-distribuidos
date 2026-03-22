from .utils import Bet
import sys
from socket import socket


class DummyProtocol:
    def __init__(self, sock: socket):
        self.sock = sock

    def send(self, bet: Bet):
        msg = "{},{},{},{},{},{}".format(
            bet.agency, bet.first_name, bet.last_name, bet.document, bet.birthdate, bet.number)
        msg_bytes = msg.encode('utf-8')
        msg_size = len(msg_bytes)
        self.sock.sendall(msg_size.to_bytes(4, byteorder=sys.byteorder))
        self.sock.sendall(msg_bytes)

    def recv(self):
        msg = self.sock.recv(4)
        if not msg:
            return None
        msg_size = int.from_bytes(msg, byteorder=sys.byteorder)
        msg = b""
        while len(msg) < msg_size:
            chunk = self.sock.recv(msg_size - len(msg))
            if not chunk:
                return None
            msg += chunk
        args = msg.decode('utf-8').split(',')
        return Bet(*args)
