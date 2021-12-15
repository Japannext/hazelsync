'''Restore the snapshot(s) of a cluster'''

from logging import getLogger

import click

from hazelsync.cli import with_cluster

log = getLogger('hazelsync')

@click.command()
@click.argument('name')
@click.argument('snapshot')
def restore(name, snapshot):
    '''Restore a cluster to a given snapshot'''
    with with_cluster(name) as cluster:
        log.debug("Starting restore")
        cluster.restore(snapshot)
