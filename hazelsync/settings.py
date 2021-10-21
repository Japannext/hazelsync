'''A module for loading settings'''

import sys
from logging import getLogger

import yaml
from pathlib import Path

log = getLogger(__name__)

class JobSettings:

    @classmethod
    def from_config(cls, name):
        '''Load a Cluster class from the config file'''
        config_file = cls.config_d / f"{name}.yaml"
        if config_file.is_file():
            with open(config_file) as f:
                config = yaml.safe_load(f.read())
        else:
            log.error("Could not read config file at %s", config_file)
            sys.exit(1)
        log.debug("Loaded config from %s", config_file)
        return cls(**config)

    pathd = Path('/etc/hazelsync.d')

    def __init__(self, name):
        path = pathd / f"{name}.yaml"
        if path.is_file():
            config = yaml.safe_load(path.read_text())
        else:
            log.error("Error reading config at %s: no such file or directory", path)
            sys.exit(1)

class GlobalSettings:

    path = '/etc/hazelsync.yaml'

    def __init__(self, path=cls.path):
        path = Path(path)
        if path.is_file():
            config = yaml.safe_load(path.read_text())
        else:
            log.error("Error reading config at %s: no such file or directory", path)
            sys.exit(1)

        self.default_backend = ''
