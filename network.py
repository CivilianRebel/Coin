import json
import threading
import traceback
import struct
import socket
import time

"""
packets
"""
version = 'vers'
verrack = 'vack'
getpeers = 'getpeers'
addr = 'addr'
inv = 'inv'

packets = [version, verrack, getpeers]
"""
start with these packets for now bc its late
and I like sleep sometimes
"""


def _debug(*args):
    print(f'[{threading.currentThread().getName()}]\t', args)


# noinspection PyBroadException
class Peer:

    def __init__(self, _id, host, port, debugging=True, max_peers=0):
        self.peer_id = _id
        self.server_host = host
        self.listen_port = port
        self.debugging = debugging
        self.max_peers = max_peers
        self.app_version = '01'
        self.running = True
        self.lock = threading.Lock()
        self.peers = []
        self.handlers = {version: self.handle_version,
                         verrack: self.handle_verrack,
                         getpeers: self.handle_get_peers,
                         addr: self.handle_addr}

    def debug(self, *args):
        if self.debugging:
            _debug(args)

    def create_server_socket(self, port=None, q=5):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', port if port else self.listen_port))
        sock.listen(q)
        return sock

    def handle_peer(self, sock):
        self.debug(f'Created new child {threading.currentThread().getName()}')
        self.debug(f'Connected to {sock.getpeername()}')

        host, port = sock.getpeername()

        peer = PeerConnection(None, host, port, sock, True)

        msg_type, data = peer.read()
        if msg_type:
            msg_type = msg_type.lower()
        if msg_type not in self.handlers:
            self.debug(f'Message type "{msg_type}" was not properly added to handlers')
        else:
            self.debug(f'Handling {msg_type} from {host}')
            self.handlers[msg_type](peer, data)
        peer.close()

    def main_loop(self):
        server = self.create_server_socket(self.listen_port)
        server.settimeout(None)

        while self.running:
            try:
                self.debug(f'Server [{self.peer_id}] {self.server_host}:{self.listen_port}')
                client_socket, client_addr = server.accept()

                thread = threading.Thread(target=self.handle_peer, args=[client_socket])
                thread.start()
            except KeyboardInterrupt:
                print('Stopping listen loop...')
                self.running = False
                break
            except:
                if self.debugging:
                    traceback.print_exc()
        self.debug('Exited main listen loop')
        server.close()

    # begin handlers
    def handle_version(self, peer_connection, data):
        peer_version, peer_id, last_block = data.split(',')
        if peer_version == self.app_version:
            # TODO: add handling for checking if peer is correct version
            pass
        peer_connection.send(verrack, '')

    def handle_verrack(self, peer_connection, data):
        # TODO: add data in peers list to verify we are allowed to talk to this peer
        pass

    def handle_get_peers(self, peer_connection, data):
        """

        :param peer_connection: Connection to the peer for writing and/or reading
        :param data: In this method this should be the number of peers to reply with
        :return: None
        """
        self.lock.acquire()
        try:
            self.debug(f'Sending list of peers to {peer_connection.host}')
            msg = {}
            for peer in self.peers:
                host, port, pid = peer['host'], peer['port'], peer['id']
                m_dict = {'host': host,
                          'port': port}
                msg[pid] = m_dict
            peer_connection.send(addr, json.dumps(msg))
        finally:
            self.lock.release()

    def handle_addr(self, peer_connection, data):
        # TODO: handle list of hosts from peer
        with self.lock:
            if len(self.peers) >= self.max_peers:
                return None
            data_dict = json.loads(data)
            for pid, entry in data_dict.items():
                if len(self.peers) < self.max_peers:
                    self.peers.append({pid: {
                        'host': entry['host'],
                        'port': entry['port']
                    }})


# noinspection PyBroadException
class PeerConnection:

    def __init__(self, name, host, port, sock=None, debug=True):
        self.name = name
        self.host = host
        self.port = port
        if sock is not None:
            self.sock = sock
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
        self.debugging = debug

    def close(self):
        self.sock.close()

    @staticmethod
    def make_msg(msg_type, msg_data):
        length = len(msg_data)
        msg = struct.pack(f'!16sL{length}s', msg_type, length, msg_data)
        return msg

    def send(self, msg_type, data):
        msg = self.make_msg(bytes(msg_type, 'utf8'), bytes(data, 'utf8'))
        self.sock.send(msg)

    def read(self):
        msg_type = ''
        msg = ''
        try:
            msg_type = self.sock.read(4)
            data = self.sock.read(4)
            msg_len = int(struct.unpack('!L', data)[0])

            while len(msg) != msg_len:
                data = self.sock.read(min(2048, msg_len - len(msg)))
                if not len(data):
                    break
                msg += data

            if len(msg) != msg_len:
                return [None, None]

        except KeyboardInterrupt:
            raise
        except:
            if self.debugging:
                traceback.print_exc()
                return [None, None]

        return [msg_type, msg]
