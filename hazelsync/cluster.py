'''Retrieve a cluster configuration'''

import logging
from logging import getLogger, FileHandler, DEBUG, Formatter, basicConfig
from datetime import datetime
from pathlib import Path

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

from hazelsync.plugin import Plugin
from hazelsync.settings import ClusterSettings
from hazelsync.reports import Report

log = getLogger('hazelsync')

def merge_statuses(slots) -> str:
    '''Return the general status given a list of slots'''
    if all(slot['status'] == 'failure' for slot in slots):
        status = 'failure'
    elif any(slot['status'] == 'failure' for slot in slots):
        status = 'partial'
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
        self.prometheus = settings.globals.prometheus
        self.backend = Plugin('backend').get(backend_type)(name=settings.name, **backend_options)
        self.job = Plugin('job').get(job_type)(name=settings.name, **job_options, backend=self.backend)
        self.job_type = job_type

        self.registry = CollectorRegistry()
        self.metrics = {
            'runtime': Gauge('runtime', 'Time the job took',
                ['action', 'cluster', 'job'], registry=self.registry),
            'job_status': Gauge('job_status', 'Status of the job',
                ['action', 'cluster', 'job'], registry=self.registry),
            'slot_status': Gauge('slot_status', 'Status of each slot',
                ['action', 'cluster', 'job', 'slot'], registry=self.registry),
        }

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
        labels = ('backup', self.name, self.job_type)
        with self.metrics['runtime'].labels(*labels).time():
            slots = self.job.backup()
        with self.metrics['runtime'].labels('snapshot', self.name, self.job_type).time():
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
        self.metrics['job_status'].labels(*labels).set(status)
        for slot in slots:
            self.metrics['slot_status'].labels(*labels, slot['slot']).set(slot['status'])
        self.publish_metrics()

    def stream(self):
        '''Stream some data to make backup faster'''
        self.config_logging('stream')
        labels = ('stream', self.name, self.job_type)
        with self.metrics['runtime'].labels(*labels).time():
            slots = self.job.stream()
        slots = self.job.stream()
        status = merge_statuses(slots)
        self.metrics['job_status'].labels(*labels).set(status)
        for slot in slots:
            self.metrics['slot_status'].labels(*labels, slot['slot']).set(slot['status'])
        self.publish_metrics()

    def publish_metrics(self, action):
        '''Send metrics to prometheus if configured'''
        if self.prometheus:
            push_to_gateway(self.prometheus, job='hazelsync', registry=self.registry)

    def restore(self, snapshot):
        '''Restore a snapshot on a cluster'''
        self.config_logging('restore')
        self.job.restore(snapshot)
