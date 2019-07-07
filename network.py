import json
import threading
import traceback
import struct
import socket
import time
import os
from uuid import uuid4

from utils import Settings

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


class Network:

    def __init__(self, host='127.0.0.1', port=25565, max_peers=200, *args, **kwargs):
        self.host = host
        self.port = port
        self.max_peers = max_peers
        self.debugging = kwargs.get('debug', False)
        if 'node_id' not in kwargs:
            self.node_id = self.establish_id()
        else:
            self.node_id = kwargs.get('node_id')
        self.config = kwargs.get('config', Settings())
        self.nodes = []
        self.listen_thread = None

    def create_listen_thread(self):
        """
        Spawns the listener thread
        :return: None
        """
        self.listen_thread = threading.Thread(target=self.listen, daemon=True)
        self.listen_thread.start()
        print('Started listener thread')

    def broadcast(self, packet):
        """
        Iterate through all nodes, for every node, connect and send packet
        :param packet: The packet to send
        :return: number of nodes we got a reply from
        """
        assert isinstance(packet, Packet), 'Packet must be a Packet() object'

    def handle_node(self, sock):
        """
        This method is called in a new thread when a node connects to us
        it handles communication between nodes
        :param sock: Socket passed from parent server
        :return: None
        """
        print(f'Created child {threading.currentThread().getName()}')
        print(f'Connected to {sock.getpeername()}')

        host, port = sock.getpeername()
        node_connection = Connection(host, port, sock)
        packet = node_connection.get_packet()
        packet.handle()

    def listen(self):
        """
        This method is called by a new thread to listen for connections on the
        host and port

        for each new connection it creates a new thread to handle the communication

        :return: None
        """
        # first create the server socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        while True:
            client_socket, client_addr = server.accept()
            handler_thread = threading.Thread(target=self.handle_node, args=[client_socket])
            handler_thread.start()

    def establish_id(self):
        """
        Creates or gets node id from config
        :return: None
        """
        if self.config.node_id is None:
            self.config.node_id = str(uuid4()).replace('-', '')
        return self.config.node_id


class Connection:

    def __init__(self, node_host, node_port, sock=None):
        self.node_host = node_host
        self.node_port = node_port
        if sock:
            self.sock = sock
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.node_host, self.node_port))

    def send_packet(self, packet):
        """
        Sends a packet to the connected node
        :param packet: Packet instance
        :return: None
        """
        assert isinstance(packet, Packet), 'Argument needs to be a Packet instance'
        self.sock.send(bytes(packet))

    def get_packet(self):
        """
        Reads a packet from the socket
        :return: Packet(packet_type, packet_payload)
        """
        msg_type = ''
        msg = ''
        try:
            msg_type = self.sock.recv(4)
            data = self.sock.recv(4)
            msg_len = int(struct.unpack('!L', data)[0])

            while len(msg) != msg_len:
                data = self.sock.recv(min(2048, msg_len - len(msg)))
                if not len(data):
                    break
                msg += data

            if len(msg) != msg_len:
                return [None, None]

        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()

        return Packet(type=msg_type, payload=msg)


class Packet(object):
    def __init__(self, **kwargs):
        self.packet_type = kwargs.get('type', None)
        if self.packet_type:
            self.packet_type = str(self.packet_type).lower()
        self.payload = kwargs.get('payload', None)
        if self.packet_type is None and self.payload is None:
            raise TypeError('This class cannot be initialized with None values')
        if not hasattr(self, f'handle_{self.packet_type}'):
            raise AttributeError(f'Handler "handle_{self.packet_type}" in packet class did not exist')

    def __bytes__(self):
        length = len(self.payload)
        msg = struct.pack(f'!16sL{length}s', bytes(self.packet_type, 'utf8'), length, bytes(self.payload, 'utf8'))
        return msg

    def __str__(self):
        return str(self.__bytes__())

    def handle(self):
        if hasattr(self, f'handle_{self.packet_type}'):
            getattr(self, f'handle_{self.packet_type}')()
        else:
            raise AttributeError(f'Could not find handler for {self.packet_type}.')

    def handle_test(self):
        print(f'Testing if this actually works\npacket_type: {self.packet_type}\npayload: {self.payload}')


class Node:
    pass


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
        self.message_queue = None
        self.peers = []
        self.handlers = {version: self.handle_version,
                         verrack: self.handle_verrack,
                         getpeers: self.handle_get_peers,
                         addr: self.handle_addr}

    def debug(self, *args):
        if self.debugging:
            _debug(args)

    def set_message_queue(self, q):
        self.message_queue = q

    def broadcast(self, msg_type, msg, t=5):
        """
        connect to each peer in list with timeout t
        :param msg_type: Type of message to send
        :param msg: Message body to send to peers
        :param t: Time to wait before moving on to the next peer
        :return: None
        """
        return None

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
            msg_type = self.sock.recv(4)
            data = self.sock.recv(4)
            msg_len = int(struct.unpack('!L', data)[0])

            while len(msg) != msg_len:
                data = self.sock.recv(min(2048, msg_len - len(msg)))
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


if __name__ == '__main__':
    # testing packet
    # this one should work fine
    p = Packet(type='test', payload='test to see if this works')
    p.handle()
    print(p)
    # this should fail
    try:
        p1 = Packet(type='bullshit_packet', payload='blah')
        p1.handle()
    except:
        print('Failed successfully')