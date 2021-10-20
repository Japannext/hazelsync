'''Local filesystem backend'''

from datetime import datetime
from pathlib import Path
from logging import getLogger

import sysrsync
from sysrsync.exceptions import RsyncError

log = getLogger(__name__)

class LocalFs:
    '''Local filesystem backend for backups. Mainly there for testing and demonstration
    purpose.
    '''
    def __init__(self, basedir: Path):
        self.basedir = basedir
        self.slotdir = basedir / 'slots'
        self.snapshotdir = basedir / 'snapshots'

        # Ensure directories
        self.slotdir.mkdir(exist_ok=True)
        self.snapshotdir.mkdir(exist_ok=True)

    def slot(self, name):
        '''Fetch a slot from the backend'''
        slot = self.slotdir / name
        if not slot.is_dir():
            log.info("Creating missing directory %s", slot)
            slot.mkdir()
        return slot

    def snapshot(self, slot):
        '''Create a snapshot. Will use rsync with hardlink mode to improve data efficiency.
        '''
        now = datetime.now().astimezone()
        snapshot_name = slot.name + '-' + now.strftime('%Y-%m-%dT%H:%M:%s')
        mysnapshot = self.snapshotdir / snapshot_name
        try:
            sysrsync.run(
                source=slot,
                destination=mysnapshot,
                options=['--link-dest', str(slot)],
            )
        except RsyncError as err:
            log.error("Snapshot %s failed: %s", snapshot_name, err)
            raise err
