import os
import json

config_location = 'settings.json'
defaults = {'node_id': None,
            'blockchain_location': 'blockchain/',
            }


class Settings:
    """
    so far the usage of the settings object is as follows

    config['blockchain_location'] = 'path/to/folder'
        this enters the value into the dictionary then saves to a file

    print(config['node_id'])
        this checks to see if we have it in memory, then double checks
        in the file then returns the value

    this class can also be used with attributes instead of like a
    dictionary


    """
    
    def load_config(self, overwrite=False, *args, **kwargs):
        d = kwargs.get('defaults', defaults)
        if os.path.exists(config_location) and not overwrite:
            with open(config_location, 'r') as file:
                temp = json.load(file)
            for key, value in temp.items():
                if key in self.__dict__:
                    if value is not self.__dict__.get(key):
                        self.__dict__[key] = value
        else:
            with open(config_location, 'w+') as file:
                json.dump(d, file)
            for key, value in d.items():
                self.__dict__[key] = value

    def save(self):
        with open(config_location, 'w+') as file:
            json.dump(self.__dict__, file)

    def __setattr__(self, key, value):
        self.__dict__[key] = value
        self.save()

    def __getattr__(self, item):
        if item not in self.__dict__:
            raise AttributeError(f'Could not find attribute {item}')
        else:
            return self.__dict__[item]

    def __getitem__(self, item):
        if item not in self.__dict__:
            raise KeyError('Could not find the key in the config')
        else:
            return self.__dict__[item]

    def __setitem__(self, key, value):
        self.__dict__[key] = value
        self.save()

    def __str__(self):
        return json.dumps(self.__dict__)


if __name__ == '__main__':
    # test setting attributes
    config = Settings()
    config.load_config(defaults=defaults, overwrite=True)
    for i in range(10):
        config.__setattr__(i, i**2)
    print(config)
