'''Retrieve a cluster configuration'''

from logging import getLogger

from hazelsync.plugin import Plugin
from hazelsync.settings import Settings

log = getLogger(__name__)

class Cluster:
    '''Class used to represent the cluster configuration for backup
    and restore'''

    def __init__(self, settings: Settings):
        '''Create a cluster class
        '''
        job_type, job_options = settings.job()
        backend_type, backend_options = settings.backend()

        self.backend = Plugin('backend').get(backend_type)(name=settings.name, **backend_options)
        self.job = Plugin('job').get(job_type)(name=settings.name, **job_options, backend=self.backend)

    def backup(self):
        '''Run the backup of a cluster'''
        slots = self.job.backup()
        for slot in slots:
            self.backend.snapshot(slot)

    def restore(self, snapshot):
        '''Restore a snapshot on a cluster'''
        self.job.restore(snapshot)
