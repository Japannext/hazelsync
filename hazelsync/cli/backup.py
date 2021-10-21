'''Backup a cluster'''

import sys
from logging import getLogger

import click

from ..cluster import Cluster

log = getLogger(__name__)

@click.command()
@click.argument('name')
def backup(name):
    '''Create a backup for a configured cluster'''
    try:
        log.debug("Initializing cluster")
        cluster = Cluster.from_config(name)
        log.debug("Cluster initialized")
        log.debug("Starting backup")
        cluster.backup()
    except Exception as err:
        log.error(err)
        sys.exit(1)
