'''Reading and writing reports'''

from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from dataclasses import dataclass
from enum import Enum
from logging import getLogger

import yaml
import dateutil.parser

REPORT_DIRECTORY = Path('/var/lib/hazelsync/reports')
TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

log = getLogger('hazelsync')

class Status(Enum):
    '''Status of a job'''
    SUCCESS = 0
    PARTIAL = 1
    FAILURE = 2

    def merge_status(self, other: 'Status') -> 'Status':
        '''Merge the status with another'''
        if self.value >= other.value:
            return self
        return other

    def to_nagios_status(self):
        '''Convert the status to a nagios status'''
        if self.value == Status.SUCCESS:
            return 'ok'
        if self.value == Status.FAILURE:
            return 'critical'
        if self.value == Status.PARTIAL:
            return 'warning'
        return 'unknown'

@dataclass
class Report:
    '''Object to represent reports'''

    directory = REPORT_DIRECTORY

    cluster: str
    job_name: str
    job_type: str
    start_time: datetime
    end_time: datetime
    status: str
    slots: List[dict]

    def serialize(self) -> str:
        '''Make the object into a string'''
        slots = [
            {
                key: str(value) if isinstance(value, Path) else value
                for key, value in slot.items()
            }
            for slot in self.slots
        ]
        data = {
            'cluster': self.cluster,
            'job_name': self.job_name,
            'job_type': self.job_type,
            'start_time': self.start_time.strftime(TIME_FORMAT),
            'end_time': self.end_time.strftime(TIME_FORMAT),
            'status': self.status,
            'slots': slots,
        }
        text = yaml.dump(data)
        return text

    @staticmethod
    def deserialize(text: str) -> 'Report':
        '''Create a report object from a string'''
        data = yaml.safe_load(text)
        try:
            kwargs = {
                'cluster': data['cluster'],
                'job_name': data['job_name'],
                'job_type': data['job_type'],
                'start_time': datetime.strptime(data['start_time'], TIME_FORMAT),
                'end_time': datetime.strptime(data['end_time'], TIME_FORMAT),
                'status': data['status'],
                'slots': data['slots'],
            }
            report = Report(**kwargs)
            return report
        except KeyError as err:
            key = err.args[0]
            raise Exception(f"Missing argument: {key}")

    @staticmethod
    def get(cluster: str,
        date_from: datetime = datetime.today() - timedelta(days=1),
        date_to: datetime = datetime.now(),
    ) -> List['Report']:
        '''Return a list of reports between two dates'''
        path = Report.directory / cluster
        if path.is_dir():
            log.debug("Directory %s exists", path)
            paths = [
                p for p in path.glob('*.yaml')
                if date_from <= dateutil.parser.parse(p.stem) <= date_to
            ]
            log.debug("Found paths: %s", paths)
        else:
            raise Exception(f"No reports found at {path}: No such directory")

        reports = []
        for path in paths:
            try:
                reports.append(Report.read(path))
            except Exception as err:
                log.error("Cannot read report at %s: %s", path, err)
                continue
        reports = [Report.read(path) for path in paths]
        return reports

    @staticmethod
    def last_report(cluster: str) -> 'Report':
        path = Report.directory / cluster
        if path.is_dir():
            log.debug("Directory %s exists", path)
            paths = list(path.glob('*.yaml'))
            log.debug("Found paths: %s", paths)
        else:
            raise Exception(f"No reports found at {path}: No such directory")
        path = sorted(paths)[-1]
        report = Report.read(path)
        return report

    @staticmethod
    def read(path: Path) -> 'Report':
        '''Read a report from a given path'''
        text = path.read_text(encoding='utf-8')
        return Report.deserialize(text)

    def make_path(self) -> Path:
        '''Create the file where the report will be stored'''
        path = Report.directory / self.cluster
        path.mkdir(exist_ok=True, parents=True)
        filename = self.start_time.strftime(TIME_FORMAT) + '.yaml'
        filepath = path / filename
        return filepath

    def write(self):
        '''Write the report to file'''
        path = self.make_path()
        text = self.serialize()
        path.write_text(text)

    def to_nagios(self, days: int) -> str:
        '''Display a line for nagios'''
        if self.status == 'success':
            status = 'OK'
        elif self.status == 'failure':
            status = 'CRITICAL'
        elif self.status == 'partial':
            status = 'WARNING'
        else:
            status = 'UNKNOWN'
        if datetime.now() >= self.start_time + timedelta(days=days):
            status = 'UNKNOWN'
        slot_success = len([s for s in self.slots if s['status'] == 'success'])
        slot_total = len(self.slots)
        return f"[{status}] {self.cluster} Slots: {slot_success}/{slot_total} succeeded"
