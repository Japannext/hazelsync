'''Local filesystem backend'''

from datetime import datetime
from logging import getLogger
from typing import Optional

from hazelsync.backend import Backend
from hazelsync.utils.rsync import rsync_run, RsyncError

log = getLogger('hazelsync')

class LocalfsBackend(Backend):
    '''Local filesystem backend for backups. Mainly there for testing and demonstration
    purpose.
    '''
    def __init__(self,
        name: str,
        path: Optional[str] = None,
        basedir: Optional[str] = None
    ):
        if path:
            self.slotdir = path / 'slots'
        elif basedir:
            self.slotdir = basedir / name / 'slots'
        else:
            raise AttributeError("localfs backend need at least one of the following argument: path or basedir")
        self.slotdir = basedir / 'slots'
        self.snapshotdir = basedir / 'snapshots'

        # Ensure directories
        self.slotdir.mkdir(exist_ok=True)
        self.snapshotdir.mkdir(exist_ok=True)

    def ensure_slot(self, name):
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
            rsync_run(
                source=slot,
                destination=mysnapshot,
                options=['--link-dest', str(slot)],
            )
        except RsyncError as err:
            log.error("Snapshot %s failed: %s", snapshot_name, err)
            raise err
