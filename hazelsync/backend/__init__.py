'''Basic backend class'''

from abc import abstractmethod
from pathlib import Path
from typing import ContextManager

from filelock import FileLock

class Backend:
    '''Abstract class for implementing a new hazelsync backend
    '''
    def lock(self, slot: Path, timeout: int = -1) -> ContextManager:
        '''Default class for handling locking a slot.
        Should return a context manager that should lock on enter,
        and release the lock on exit.
        '''
        return FileLock(slot / '.hazesync.lock', timeout)

    @abstractmethod
    def ensure_slot(self, name: str) -> Path:
        pass

    @abstractmethod
    def snapshot(self, slot):
        pass
