'''Restore the snapshot(s) of a cluster'''

import sys
from logging import getLogger

import click

from ..cluster import Cluster

log = getLogger(__name__)

@click.command()
@click.argument('name')
@click.argument('snapshot')
def restore(name, snapshot):
    '''Restore a cluster to a given snapshot'''
    try:
        log.debug("Initializing cluster")
        cluster = Cluster.from_config(name)
        log.debug("Cluster initialized")
        log.debug("Starting restore")
        cluster.restore(snapshot)
    except Exception as err:
        log.error(err)
        sys.exit(1)
