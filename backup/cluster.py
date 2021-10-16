'''Retrieve a cluster configuration'''

from pathlib import Path

import yaml

from .type import BackupType, get_backup_job

class Cluster:
    '''Class used to represent the cluster configuration for backup
    and restore'''
    config_path = Path(f"/etc/{__name__}.yaml")

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
        config = yaml.safe_load(cls.config_path)
        clusters = config.get('clusters', {})
        myconfig = clusters.get(name, {})
        return cls(**myconfig)

    def backup(self):
        '''Run the backup of a cluster'''
        snapshot = self.job.backup()

    def restore(self, snapshot):
        '''Restore a snapshot on a cluster'''
        raise NotImplementedError()
