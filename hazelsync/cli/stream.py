'''Backup a cluster'''

import sys

import click

from hazelsync.cluster import Cluster
from hazelsync.settings import ClusterSettings

@click.command()
@click.argument('name')
def stream(name):
    '''Pull some data to ease the backup speed'''
    settings = ClusterSettings(name)
    log = settings.globals.logger()
    log.debug("Loaded cluster configuration for %s", name)
    try:
        cluster = Cluster(settings)
        log.debug("Cluster initialized")
        log.debug("Starting backup")
        cluster.stream()
    except Exception as err:
        log.exception(err)
        sys.exit(1)
