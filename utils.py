import os
import json


class Settings:
    """
    so far the usage of the settings object is as follows

    config['blockchain_location'] = 'path/to/folder'
        this enters the value into the dictionary then saves to a file

    print(config['node_id'])
        this checks to see if we have it in memory, then double checks
        in the file then returns the value

    """

    def __init__(self, config_location='config.json'):
        self.location = config_location
        self.loaded = False
        self.config = {'node_id': None,
                       'port': 25565,
                       'max_peers': 200,
                       'blockchain_location': 'blockchain/'}

    def load_config(self, loc=None):
        if loc:
            self.location = loc

        if os.path.exists(self.location):
            with open(self.location, 'r') as file:
                self.config = json.load(file)
                self.loaded = True
        else:
            with open(self.location, 'w+') as file:
                json.dump(self.config, file)
                self.loaded = True

    def save(self):
        with open(self.location, 'w+') as file:
            json.dump(self.config, file)

    def __getitem__(self, item):
        if item not in self.config.keys():
            self.load_config()
            if item not in self.config.keys():
                raise KeyError('Could not find the key in the config')
        else:
            return self.config[item]

    def __setitem__(self, key, value):
        self.config[key] = value
        self.save()
