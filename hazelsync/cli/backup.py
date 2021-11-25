'''Backup a cluster'''

import sys

import click

from hazelsync.cluster import Cluster
from hazelsync.settings import ClusterSettings

@click.command()
@click.argument('name')
def backup(name):
    '''Create a backup for a configured cluster'''
    settings = ClusterSettings(name)
    log = settings.globals.logger()
    log.debug("Loaded cluster configuration for %s", name)
    try:
        cluster = Cluster(settings)
        log.debug("Cluster initialized")
        log.debug("Starting backup")
        cluster.backup()
    except Exception as err:
        log.exception(err)
        sys.exit(1)
