'''ZFS backend'''

import subprocess
from typing import Optional
from datetime import datetime
from logging import getLogger
from pathlib import Path

from . import Backend

log = getLogger(__name__)

class ZfsError(RuntimeError): pass

def run(cmd):
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    if proc.returncode != 0:
        stderr = proc.stderr
        cmd_line = ' '.join(cmd)
        raise ZfsError(f"Failed to run `{cmd_line}`: {stderr}")
    return proc

def create_dataset(mount_point: Path):
    '''Create a dataset'''
    dataset = str(mount_point)[1:]
    cmd = ['zfs', 'create', dataset]
    run(cmd)

def list_datasets(dataset: Optional[str] = None):
    '''List the datasets available under a given path/name'''
    cmd = ['zfs', 'list', '-H', '-r', '-t', 'filesystem', str(dataset)]
    proc = run(cmd)
    datasets = {}
    for line in proc.stdout.strip().split('\n'):
        name, used, avail, refer, mountpoint = line.split('\t')
        dataset = {'name': name, 'used': used, 'avail': avail, 'refer': refer}
        datasets[Path(mountpoint)] = dataset
    return datasets

def snapshot_dataset(mount_point: Path, properties: dict = {}):
    dataset = str(mount_point)[1:]
    property_list = []
    for key, value in properties.items():
        property_list += ['-o', f"{key}={value}"]
    cmd = ['zfs', 'snapshot', '-r', dataset, *property_list]
    run(cmd)

class Zfs(Backend):
    '''Local filesystem backend for backups. Mainly there for testing and demonstration
    purpose.
    '''
    def __init__(self, path: str):
        self.slotdir = Path(path)
        if not self.slotdir.is_dir():
            log.info("Creating missing dataset %s", self.slotdir)
            create_dataset(self.slotdir)
        self.datasets = list_datasets(self.slotdir)

    def ensure_slot(self, name) -> Path:
        '''Fetch a slot from the backend'''
        slot = self.slotdir / name
        if slot not in self.datasets:
            log.info("Creating missing dataset %s", slot)
            create_dataset(slot)
        return slot

    def snapshot(self, slot):
        '''Create a ZFS snapshot.
        '''
        log.info("Running ZFS snapshot for %s", slot.name)
        now = datetime.now().astimezone()
        snapshot_name = slot.name + '@' + now.strftime('%Y-%m-%dT%H:%M:%S')
        mysnapshot = self.slotdir / snapshot_name
        try:
            snapshot_dataset(mysnapshot)
        except ZfsError as err:
            log.error("Snapshot %s failed: %s", mysnapshot, err)
            raise err

BACKEND = Zfs
