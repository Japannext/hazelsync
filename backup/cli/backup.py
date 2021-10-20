'''Backup a cluster'''

from logging import getLogger

import click

from ..cluster import Cluster

log = getLogger(__name__)

@click.command()
@click.argument('name')
def backup(name):
    '''Create a backup for a configured cluster'''
    log.debug("Initializing cluster")
    cluster = Cluster.from_config(name)
    log.debug("Cluster initialized")
    log.debug("Starting backup")
    cluster.backup()