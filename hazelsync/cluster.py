'''Retrieve a cluster configuration'''

import logging
from logging import getLogger, FileHandler, DEBUG, Formatter, basicConfig
from datetime import datetime
from pathlib import Path

from hazelsync.plugin import Plugin
from hazelsync.settings import ClusterSettings
from hazelsync.reports import Report
from hazelsync.metrics import Gauge, Timer

log = getLogger('hazelsync')

PROM_STATUS_MAP = {
    'success': 0,
    'failure': 1,
    'partial': 2,
    'locked': 3,
    'unknown': 4
}

def merge_statuses(slots) -> str:
    '''Return the general status given a list of slots'''
    if all(slot['status'] == 'failure' for slot in slots):
        status = 'failure'
    elif any(slot['status'] == 'failure' for slot in slots):
        status = 'partial'
    elif any(slot['status'] == 'locked' for slot in slots):
        status = 'locked'
    elif all(slot['status'] == 'success' for slot in slots):
        status = 'success'
    else:
        status = 'unknown'
    return status

class Cluster:
    '''Class used to represent the cluster configuration for backup
    and restore'''

    def __init__(self, settings: ClusterSettings):
        '''Create a cluster class
        '''
        job_type, job_options = settings.job()
        backend_type, backend_options = settings.backend()

        self.name = settings.name
        self.backend = Plugin('backend').get(backend_type)(name=settings.name, **backend_options)
        self.job = Plugin('job').get(job_type)(name=settings.name, **job_options, backend=self.backend)
        self.job_type = job_type
        # Metrics
        self.engine = settings.globals.metrics
        self.runtime = Timer('runtime',
            tags={'action': None, 'cluster': self.name, 'job': self.job_type},
            desc='Time the job took', engine=self.engine)
        self.job_status = Gauge('job_status',
            tags={'action': None, 'cluster': self.name, 'job': self.job_type},
            desc='Status of the job', engine=self.engine)
        self.slot_status = Gauge('slot_status',
            tags={'action': None, 'cluster': self.name, 'job': self.job_type, 'slot': None},
            desc='Status of each slot', engine=self.engine)

    def config_logging(self, action: str):
        '''Configure the logging'''
        path = Path(f'/var/log/hazelsync/{self.name}')
        path.mkdir(exist_ok=True, parents=True)
        if action in ['stream']:
            now = datetime.now().strftime('%Y-%m-%d')
        else:
            now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        filename = path / f"{action}-{now}.log"
        formatter = Formatter('%(asctime)s %(levelname)s: %(message)s')
        handler = FileHandler(filename)
        handler.setLevel(DEBUG)
        handler.setFormatter(formatter)
        log.addHandler(handler)

    def backup(self):
        '''Run the backup of a cluster'''
        self.config_logging('backup')
        start_time = datetime.now()
        with self.runtime.time(action='backup'):
            slots = self.job.backup()
        with self.runtime.time(action='snapshot'):
            for slot in slots:
                if slot['status'] == 'success':
                    self.backend.snapshot(slot['slot'])
        end_time = datetime.now()
        status = merge_statuses(slots)
        report = Report(
            cluster=self.name,
            job_name=self.job_type,
            job_type='backup',
            start_time=start_time,
            end_time=end_time,
            status=status,
            slots=slots,
        )
        report.write()
        self.job_status.set(PROM_STATUS_MAP[status], action='backup')
        for slot in slots:
            self.slot_status.set(PROM_STATUS_MAP[slot['status']], action='backup', slot=slot['slot'])
        self.engine.flush()

    def stream(self):
        '''Stream some data to make backup faster'''
        self.config_logging('stream')
        with self.runtime.time(action='stream'):
            slots = self.job.stream()
        slots = self.job.stream()
        status = merge_statuses(slots)
        self.job_status.set(PROM_STATUS_MAP[status], action='stream')
        for slot in slots:
            self.slot_status.set(PROM_STATUS_MAP[slot['status']], action='stream', slot=slot['slot'])
        self.engine.flush()

    def restore(self, snapshot):
        '''Restore a snapshot on a cluster'''
        self.config_logging('restore')
        with self.runtime.time(action='restore'):
            self.job.restore(snapshot)
        self.engine.flush()
