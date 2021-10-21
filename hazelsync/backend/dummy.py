'''Dummy backend to use for testing'''

from logging import getLogger

log = getLogger(__name__)

class Dummy:
    '''Dummy backend for testing purposes.'''
    def __init__(self):
        log.info("Initialized Dummy backend")
    def ensure_slot(self, name):
        '''Dummy function to ensure the slot exists. Only logs.'''
        log.info("Ensured dummy slot existence for %s", name)
    def snapshot(self, slot):
        '''Dummy function to snapshot. Only logs.'''
        log.info("Took dummy snapshot for slot %s", slot)

BACKEND = Dummy
