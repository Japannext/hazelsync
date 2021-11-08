'''Retrieve a cluster configuration'''

from logging import getLogger, FileHandler, DEBUG, Formatter, basicConfig
from datetime import datetime
from pathlib import Path

from hazelsync.plugin import Plugin
from hazelsync.settings import Settings

log = getLogger('hazelsync')

class Cluster:
    '''Class used to represent the cluster configuration for backup
    and restore'''

    def __init__(self, settings: Settings):
        '''Create a cluster class
        '''
        job_type, job_options = settings.job()
        backend_type, backend_options = settings.backend()

        self.name = settings.name
        self.backend = Plugin('backend').get(backend_type)(name=settings.name, **backend_options)
        self.job = Plugin('job').get(job_type)(name=settings.name, **job_options, backend=self.backend)

    def config_logging(self, action: str):
        '''Configure the logging'''
        path = Path(f'/var/log/hazelsync/{self.name}')
        path.mkdir(exist_ok=True, parents=True)
        now = datetime.now().strftime('%Y-%m-%dT%H%M%S')
        filename = path / f"{now}-{action}.log"
        formatter = Formatter('%(asctime)s %(levelname)s: %(message)s')
        handler = FileHandler(filename)
        handler.setLevel(DEBUG)
        handler.setFormatter(formatter)
        log.addHandler(handler)

    def backup(self):
        '''Run the backup of a cluster'''
        self.config_logging('backup')
        slots = self.job.backup()
        for slot in slots:
            self.backend.snapshot(slot)

    def stream(self):
        '''Stream some data to make backup faster'''
        path = Path(f"/var/log/hazelsync/{self.name}")
        path.mkdir(exist_ok=True, parents=True)
        today = datetime.now().strftime('%Y-%m-%d')
        filename = path / f"{today}-stream.log"
        formatter = Formatter('%(asctime)s %(levelname)s: %(message)s')
        handler = FileHandler(filename)
        handler.setLevel(DEBUG)
        handler.setFormatter(formatter)
        log.addHandler(handler)
        self.job.stream()

    def restore(self, snapshot):
        '''Restore a snapshot on a cluster'''
        self.config_logging('restore')
        self.job.restore(snapshot)
