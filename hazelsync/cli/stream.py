'''Backup a cluster'''

from logging import getLogger

import click

from hazelsync.cli import with_cluster

log = getLogger('hazelsync')

@click.command()
@click.argument('name')
def stream(name):
    '''Pull some data to ease the backup speed'''
    with with_cluster(name) as cluster:
        log.info("Running hazel stream for %s", name)
        cluster.stream()
