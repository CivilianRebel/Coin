import json
import time

from utils import Settings


class Handler:

    def __init__(self, *args, **kwargs):
        self.config = kwargs.get('config', Settings())
        self.network = kwargs.get('network', None)

        assert self.network is not None, 'Network is a required argument'

        self.config.load_config()

    def handle_test(self, connection, packet_data):
        print(f'omg handling test\n {packet_data}')
        return self

    def handle_versack(self, connection, packet_data):
        pass

    def handle_version(self, connection, packet_data):
        """
        we've received a packet that contains their version information
        we send back a versack if our versions cooperate
        then we send a version packet back to the node and wait for the versack
        :param connection: connection object that connects to node
        :param packet_data: should be a dict
            {node_id, last_block_hash, major_version, minor_version}
        :return: Boolean: is this node compatible
        """
        packet_dict = json.loads(str(packet_data, encoding='utf8'))
        node_id = packet_dict['node_id']
        version = packet_dict['version']
        node_last_hash = packet_dict['last_block_hash']

        if version is self.config.version:
            # good that means we can connect
            # send versack
            connection.send(packet_type='versack', co_op=True)
            connection.send(packet_type='version',
                            node_id=self.config.node_id,
                            last_block_hash=self.config.last_block_hash,
                            version=self.config.version,
                            timestamp=time.time())



