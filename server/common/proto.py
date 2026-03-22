from .utils import Bet
import sys
import struct
from socket import socket, htonl, ntohl

MAX_UINT16_VALUE = 2**16-1

class DummyProtocol:
    def __init__(self, sock: socket):
        self.sock = sock
        
    def read(self, size: int):
        msg = b""
        while len(msg) < size:
            chunk = self.sock.recv(size - len(msg))
            if not chunk:
                return None
            msg += chunk
        return msg

    def send(self, bet: Bet):
        msg = "{},{},{},{},{},{}".format(
            bet.agency, bet.first_name, bet.last_name, bet.document, bet.birthdate, bet.number)
        msg_bytes = msg.encode('utf-8')
        msg_size = len(msg_bytes)
        
        if msg_size > MAX_UINT16_VALUE:
            raise ValueError("Message too long")
        
        self.sock.sendall(struct.pack('>H', htonl(msg_size)))
        self.sock.sendall(msg_bytes)

    def recv(self):
        msg = self.read(2)
        if not msg:
            return None
        msg_size = ntohl(struct.unpack(">H", msg)[0])
        msg = self.read(msg_size)
        args = msg.decode('utf-8').split(',')
        return Bet(*args)
