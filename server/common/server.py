import socket
import logging
import signal
from threading import Thread, Lock, Barrier, BrokenBarrierError
from typing import Any

from .utils import store_bets, load_bets, has_won
from .proto import DummyProtocol, methods

bets_lock = Lock()

class Connection(Thread):
    def __init__(self, sock: socket.socket, addr: Any, lottery_barrier: Barrier):
        super().__init__()
        self.sock = sock
        self.addr = addr
        self.proto = DummyProtocol()
        self.closed = False
        self.lottery_barrier = lottery_barrier
        self.agency = None
        self.start()
        
    def run(self):
        while not self.closed:
            try:
                method = self.proto.read(self.sock, 1)
                if not method:
                    logging.info("Client disconnected gracefully")
                    self.close()
                    break
                
                method = method.decode('utf-8')
                if method in methods:
                    getattr(self, f'handle_{methods[method]}')()
                else:
                    logging.error(f"Unknown method {method} from client {self.addr[0]}")
                    
            except ConnectionResetError:
                logging.error(f"Connection reset by client {self.addr[0]}")
                self.close()
                
    def handle_batch(self):
        batch = self.proto.recv_batch(self.sock)
        if not batch:
            logging.info("Client disconnected gracefully")
            self.close()
            return
        
        bets, batch_size = batch
        if len(bets) > 0:
            if not self.agency:
                self.agency = bets[0].agency
            if len(bets) == batch_size:
                logging.info(f'action: apuesta_recibida | result: success | cantidad: {batch_size}')
            else:
                logging.info(f'action: apuesta_recibida | result: fail | cantidad: {batch_size}')
            
            with bets_lock:
                store_bets(bets)                    
            self.proto.ack(self.sock, bets[-1])
            
    def handle_winners(self):
        try:
            logging.info(f"Waiting for {self.lottery_barrier.parties} clients to reach lottery barrier")
            self.lottery_barrier.wait()
        except BrokenBarrierError:
            logging.error("Lottery barrier broken, cannot determine winners")
            self.close()
            return
        
        with bets_lock:
            all_bets = load_bets()
        
        winners = [bet for bet in all_bets if has_won(bet) and bet.agency == self.agency]
        self.proto.send_batch(self.sock, winners)
        
    def close(self):
        if not self.closed:
            self.closed = True
            self.sock.close()

class Server:
    def __init__(self, port, listen_backlog, n_clients):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.connections = []
        self.lottery_barrier = Barrier(n_clients)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)
        while True:
            client_sock, addr = self.__accept_new_connection()
            self.connections.append(Connection(client_sock, addr, self.lottery_barrier))

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: acceptconnections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: acceptconnections | result: success | ip: {addr[0]}')
        return c, addr
    
    def sig_handler(self, signum, frame):
        if signum == signal.SIGINT:
            logging.info("Keyboard Interrupt detected, exiting...")
        else:
            logging.info("Server forcefully terminated, exiting...")
        self.exit()
    
    def exit(self):
        for conn in self.connections:
            conn.close()
            conn.join()
        self._server_socket.close()
        self.lottery_barrier.abort()
        exit(0)
