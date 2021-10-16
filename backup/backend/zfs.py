'''ZFS backend'''

from datetime import datetime
from logging import getLogger
from pathlib import Path

from libzfs_core import lzc_snapshot
from libzfs_core.exceptions import SnapshotFailure

log = getLogger(__name__)

class Zfs:
    '''Local filesystem backend for backups. Mainly there for testing and demonstration
    purpose.
    '''
    def __init__(self, basedir: Path):
        self.basedir = basedir
        self.slotdir = basedir

    def slot(self, name):
        '''Fetch a slot from the backend'''
        slot = self.slotdir / name
        return slot

    def snapshot(self, slot):
        '''Create a ZFS snapshot.
        '''
        now = datetime.now().astimezone()
        snapshot_name = slot.name + '@' + now.strftime('%Y-%m-%dT%H:%M:%s')
        mysnapshot = self.slotdir / snapshot_name
        try:
            lzc_snapshot([mysnapshot], {'compression': True})
        except SnapshotFailure as err:
            log.error("Snapshot %s failed: %s", mysnapshot, err)
            raise err
