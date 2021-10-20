'''Retrieve a cluster configuration'''

import sys
from pathlib import Path
from logging import getLogger
from importlib import import_module

import yaml

from .backend import Backend
from .job import Job
#from .utils import find_class

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
        try:
            backend_modname = f"backup.backend.{backend_type}"
            log.debug("Attempting to load %s", backend_modname)
            backend_module = import_module(backend_modname)
            backend_class = backend_module.BACKEND
            log.debug("Found backend class %s", backend_class)
            self.backend = backend_class(**backend_options)
        except Exception as err:
            raise err
        try:
            job_modname = f"backup.job.{job_type}"
            log.debug("Attempting to load %s", job_modname)
            job_module = import_module(job_modname)
            job_class = job_module.JOB
            log.debug("Found job class %s", job_class)
            self.job = job_class(**job_options, backend=self.backend)
        except Exception as err:
            raise err

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

    def backup(self):
        '''Run the backup of a cluster'''
        slots = self.job.backup()
        for slot in slots:
            self.backend.snapshot(slot)

    def restore(self, snapshot):
        '''Restore a snapshot on a cluster'''
        raise NotImplementedError()
