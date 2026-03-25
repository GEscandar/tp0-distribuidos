from .utils import Bet
import struct
from socket import socket

MAX_UINT16_VALUE = 2**16-1
MSG_SIZE_BYTE_LEN = 2

class DummyProtocol:
        
    def read(self, sock: socket, size: int):
        msg = b""
        while len(msg) < size:
            chunk = sock.recv(size - len(msg))
            if not chunk:
                return None
            msg += chunk
        return msg
    
    def send_bytes(self, sock: socket, buf: bytes):
        msg_size = len(buf)
        
        if msg_size > MAX_UINT16_VALUE:
            raise ValueError("Message too long")
        
        sock.sendall(struct.pack('>H', msg_size))
        sock.sendall(buf)

    def send(self, sock: socket, bet: Bet):
        msg = "{},{},{},{},{},{}".format(
            bet.agency, bet.first_name, bet.last_name, bet.document, bet.birthdate, bet.number)
        self.send_bytes(sock, msg.encode('utf-8'))
        
    def ack(self, sock: socket, bet: Bet):
        msg = "{},{}".format(bet.document, bet.number)
        self.send_bytes(sock, msg.encode('utf-8'))

    def recv(self, sock: socket):
        msg = self.read(sock, MSG_SIZE_BYTE_LEN)
        if not msg:
            return None
        
        msg_size = struct.unpack(">H", msg)[0]
        msg = self.read(sock, msg_size)
        if not msg:
            return None
        
        args = msg.decode('utf-8').split(',')
        return Bet(*args)
    
    def recv_batch(self, sock: socket):
        msg = self.read(sock, MSG_SIZE_BYTE_LEN)
        if not msg:
            return None
        
        batch_size = struct.unpack(">H", msg)[0]
        bets = []
        for _ in range(batch_size):
            bet = self.recv(sock)
            if bet is None:
                break
            bets.append(bet)
            
        return bets, batch_size
