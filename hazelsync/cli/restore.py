'''Restore the snapshot(s) of a cluster'''

import sys
from logging import getLogger

import click

from hazelsync.cluster import Cluster
from hazelsync.settings import Settings

log = getLogger(__name__)

@click.command()
@click.argument('name')
@click.argument('snapshot')
def restore(name, snapshot):
    '''Restore a cluster to a given snapshot'''
    try:
        log.debug("Initializing cluster")
        settings = Settings.parse(name)
        cluster = Cluster(settings)
        log.debug("Cluster initialized")
        log.debug("Starting restore")
        cluster.restore(snapshot)
    except Exception as err:
        log.error(err)
        sys.exit(1)
