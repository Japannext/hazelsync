'''Basic backend class'''

from abc import abstractmethod
from pathlib import Path
from typing import ContextManager

from filelock import FileLock

class Backend:
    '''Abstract class for implementing a new hazelsync backend
    '''

    @staticmethod
    def lock(slot: Path, timeout: int = -1) -> ContextManager:
        '''Default class for handling locking a slot.
        Should return a context manager that should lock on enter,
        and release the lock on exit.
        '''
        # pylint: disable=abstract-class-instantiated
        return FileLock(slot / '.hazesync.lock', timeout)

    @abstractmethod
    def ensure_slot(self, name: str) -> Path:
        '''Make sure the slot is created if it needs bootstrapping'''

    @abstractmethod
    def snapshot(self, slot):
        '''Perform a snapshot of a slot'''
