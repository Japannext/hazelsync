'''Base CLI'''

import click

from .backup import backup
from ..cluster import Cluster

@click.group()
@click.option('-c', '--config', help='Override the default config')
def cli(config):
    '''Simple backup/restore program'''
    Cluster.config_path = config

cli.add_command(backup)
