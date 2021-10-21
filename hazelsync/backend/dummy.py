'''Dummy backend to use for testing'''

from logging import getLogger

log = getLogger(__name__)

class Dummy:
    def __init__(self):
        log.info("Initialized Dummy backend")
    def ensure_slot(self, name):
        log.info("Ensured dummy slot existence for %s", name)
    def snapshot(self, slot):
        log.info("Took dummy snapshot for slot %s", slot)

BACKEND = Dummy
