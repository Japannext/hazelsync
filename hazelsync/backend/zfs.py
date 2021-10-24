'''ZFS backend'''

from datetime import datetime
from logging import getLogger
from pathlib import Path

from filelock import FileLock

from hazelsync.backend import Backend
from hazelsync.utils.zfs import *

log = getLogger(__name__)

class Zfs(Backend):
    '''Local filesystem backend for backups. Mainly there for testing and demonstration
    purpose.
    '''
    def __init__(self,
        name: str,
        path: str = None,
        basedir: str = None,
    ):
        if basedir:
            self.slotdir = Path(basedir) / name
        elif path:
            self.slotdir = Path(path)
        else:
            raise AttributeError("zfs backend need at least one of the following arguments: path or basedir")
        self.datasets = zfs_list(self.slotdir)
        self.ensure_cluster()

    def ensure_cluster(self):
        '''Ensure the cluster has its dataset created with the proper settings'''
        if not self.slotdir.is_dir():
            log.info("Creating missing dataset %s", self.slotdir)
            zfs_create(self.slotdir)

    def ensure_slot(self, name: str) -> Path:
        '''Ensure a given slot has its dataset created and return its path'''
        slot = self.slotdir / name
        if slot not in self.datasets:
            log.info("Creating missing dataset %s", slot)
            zfs_create(slot)
        return slot

    def snapshot(self, slot: Path):
        '''Create a ZFS snapshot.
        '''
        if self.slotdir not in slot.parents:
            raise Exception(f"Cannot snapshot {slot}: not a sub-directory of {self.slotdir}")
        log.info("Running ZFS snapshot for %s", slot.name)
        now = datetime.now().astimezone()
        snapshot_name = slot.name + '@' + now.strftime('%Y-%m-%dT%H:%M:%S')
        mysnapshot = self.slotdir / snapshot_name
        try:
            zfs_snapshot(mysnapshot)
        except ZfsError as err:
            log.error("Snapshot %s failed: %s", mysnapshot, err)
            raise err
