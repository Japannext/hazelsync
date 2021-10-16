'''Backup a cluster'''

import click

from ..cluster import Cluster

@click.command()
@click.argument('name')
def backup(name):
    '''Create a backup for a configured cluster'''
    cluster = Cluster.from_config(name)
    cluster.backup()
