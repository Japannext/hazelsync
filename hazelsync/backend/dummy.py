'''Dummy backend to use for testing'''

from logging import getLogger
from pathlib import Path
from tempfile import mkdtemp

from filelock import FileLock

from hazelsync.backend import Backend

log = getLogger(__name__)

class Dummy(Backend):
    '''Dummy backend for testing purposes.'''
    def __init__(self, name:str=None, tmp_dir=None):
        log.info("Initialized Dummy backend")
        if tmp_dir:
            self.tmp_dir = tmp_dir
        else:
            self.tmp_dir = Path(mkdtemp())

    def ensure_slot(self, name):
        '''Dummy function to ensure the slot exists. Only logs.'''
        log.info("Ensured dummy slot existence for %s", name)
        slot = self.tmp_dir / name
        slot.mkdir(exist_ok=True)
        return slot

    def snapshot(self, slot):
        '''Dummy function to snapshot. Only logs.'''
        log.info("Took dummy snapshot for slot %s", slot)
        return slot
