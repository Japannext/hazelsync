'''Restore the snapshot(s) of a cluster'''

import sys

import click

from hazelsync.cluster import Cluster
from hazelsync.settings import ClusterSettings

@click.command()
@click.argument('name')
@click.argument('snapshot')
def restore(name, snapshot):
    '''Restore a cluster to a given snapshot'''
    settings = ClusterSettings(name)
    log = settings.globals.logger()
    log.debug("Loaded cluster configuration for %s", name)
    try:
        cluster = Cluster(settings)
        log.debug("Cluster initialized")
        log.debug("Starting backup")
        cluster.restore(snapshot)
    except Exception as err:
        log.exception(err)
        sys.exit(1)
