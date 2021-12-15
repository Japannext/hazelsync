'''Backup a cluster'''

from logging import getLogger

import click

from hazelsync.cli import with_cluster

log = getLogger('hazelsync')

@click.command()
@click.argument('name')
def backup(name):
    '''Create a backup for a configured cluster'''
    with with_cluster(name) as cluster:
        log.debug("Starting backup")
        cluster.backup()
