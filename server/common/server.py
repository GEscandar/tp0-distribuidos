import socket
import logging
import signal
from threading import Thread
import threading
from .utils import store_bets

from server.common.proto import DummyProtocol

bets_lock = threading.Lock()

class Connection(Thread):
    def __init__(self, sock: socket.socket):
        super().__init__()
        self.proto = DummyProtocol(sock)
        self.closed = False
        self.start()
        
    def run(self):
        while not self.closed:
            try:
                # TODO: Modify the receive to avoid short-reads
                msg = self.proto.recv()
                if not msg:
                   logging.info("Client disconnected gracefully")
                   self.close()
                   break
                addr = self.sock.getpeername()
                logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
                with bets_lock:
                    store_bets(msg)
                logging.info(f"action: apuesta_almacenada | result: success | dni: {msg.document} | numero: {msg.number}")
                # TODO: Modify the send to avoid short-writes
                self.proto.send(msg)
            except ConnectionResetError:
                logging.error(f"Connection reset by client {addr[0]}")
                self.close()
        
    def close(self):
        if not self.closed:
            self.sock.close()
            self.closed = True

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._connections = []

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
            client_sock = self.__accept_new_connection()
            self._connections.append(Connection(client_sock))

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
    
    def sig_handler(self, signum, frame):
        if signum == signal.SIGINT:
            logging.info("Keyboard Interrupt detected, exiting...")
        else:
            logging.info("Server forcefully terminated, exiting...")
        self.exit()
    
    def exit(self):
        for conn in self._connections:
            conn.close()
            conn.join()
        self._server_socket.close()
        exit(0)
