'''Retrieve a cluster configuration'''

import sys
from pathlib import Path
from logging import getLogger
from importlib import import_module

import yaml

from .backend import Backend
from .job import Job
from .plugin import Plugin

package_name = __name__.split('.')[0]
log = getLogger(package_name)

class Cluster:
    '''Class used to represent the cluster configuration for backup
    and restore'''
    config_path = Path(f"/etc/{package_name}.yaml")
    config_d = Path(f"/etc/{package_name}.d")

    def __init__(self,
        name: str,
        job_type: str = None,
        job_options: dict = {},
        backend_type: str = None,
        backend_options: dict = {},
        ):
        '''Create a cluster class
        :param name: The name of the cluster.
        '''
        self.name = name
        self.backend = Plugin('backend').get(backend_type)(**backend_options)
        self.job = Plugin('job').get(job_type)(**job_options, backend=self.backend)

    @classmethod
    def from_config(cls, name):
        '''Load a Cluster class from the config file'''
        config_file = cls.config_d / f"{name}.yaml"
        if config_file.is_file():
            config = yaml.safe_load(config_file.read_text())
        else:
            log.error("Could not read config file at %s", config_file)
            sys.exit(1)
        log.debug("Loaded config from %s", config_file)
        return cls(**config)

    def backup(self):
        '''Run the backup of a cluster'''
        slots = self.job.backup()
        for slot in slots:
            self.backend.snapshot(slot)

    def restore(self, snapshot, options={}):
        '''Restore a snapshot on a cluster'''
        self.job.restore(snapshot, options)
