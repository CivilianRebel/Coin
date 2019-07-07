import os
import json


class Settings:

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
        else:
            with open(self.location, 'w+') as file:
                json.dump(self.config, file)

    def save(self):
        with open(self.location, 'w+') as file:
            json.dump(self.config, file)

    def __getitem__(self, item):
        if item not in self.config.keys():
            if self.loaded:
                raise KeyError('Key was not found, maybe you forgot to call the load function?')
        else:
            return self.config[item]

    def __setitem__(self, key, value):
        self.config[key] = value
        self.save()