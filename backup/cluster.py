'''Retrieve a cluster configuration'''

import sys
from pathlib import Path
from logging import getLogger

import yaml

from .type import BackupType, get_backup_job

package_name = __name__.split('.')[0]
log = getLogger(package_name)

class Cluster:
    '''Class used to represent the cluster configuration for backup
    and restore'''
    config_path = Path(f"/etc/{package_name}.yaml")
    config_d = Path(f"/etc/{package_name}.d")

    def __init__(self, name: str, backup_type: BackupType, backup_options: dict):
        '''Create a cluster class
        :param name: The name of the cluster.
        :param backup_type: The type of backup to do.
        :param backup_options The options to pass to the backup job
        '''
        self.name = name
        job_class = get_backup_job(backup_type)
        self.job = job_class(**backup_options)

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
        snapshot = self.job.backup()

    def restore(self, snapshot):
        '''Restore a snapshot on a cluster'''
        raise NotImplementedError()
