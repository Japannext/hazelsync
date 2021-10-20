'''Base CLI'''

import sys
import logging

import click

from .backup import backup
from ..cluster import Cluster

log_format = '%(asctime)s %(levelname)s %(name)s %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=log_format)
log = logging.getLogger(__name__)

@click.group()
@click.option('-c', '--config', help='Override the default config')
def cli(config):
    '''Simple backup/restore program'''
    Cluster.config_path = config

cli.add_command(backup)
