'''Utils for CLI'''

import sys
from contextlib import contextmanager

from hazelsync.cluster import Cluster
from hazelsync.settings import ClusterSettings

@contextmanager
def with_cluster(name):
    '''Context to execute something with a prepared cluster'''
    settings = ClusterSettings(name)
    log = settings.globals.logger()
    log.debug("Loaded cluster configuration for %s", name)
    try:
        cluster = Cluster(settings)
        log.debug("Cluster initialized")
        yield cluster
    except Exception as err:
        log.exception(err)
        sys.exit(1)
