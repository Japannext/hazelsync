'''Backup a cluster'''

import sys
from logging import getLogger

import click

from hazelsync.cluster import Cluster
from hazelsync.settings import Settings

log = getLogger('hazelsync')

@click.command()
@click.argument('name')
def stream(name):
    '''Pull some data to ease the backup speed'''
    try:
        log.debug("Initializing cluster")
        settings = Settings.parse(name)
        settings.setup_logging('stream')
        cluster = Cluster(settings)
        log.debug("Cluster initialized")
        log.debug("Starting backup")
        cluster.stream()
    except Exception as err:
        log.exception(err)
        sys.exit(1)
