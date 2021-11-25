'''Base CLI'''

import sys
import logging

import click

from hazelsync.cli.backup import backup
from hazelsync.cli.restore import restore
from hazelsync.cli.stream import stream
from hazelsync.cli.nagios import nagios
from hazelsync.cluster import Cluster

log_format = '%(asctime)s %(levelname)s %(name)s %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=log_format)
log = logging.getLogger('hazelsync')

@click.group()
@click.option('-c', '--config', help='Override the default config')
def cli(config):
    '''Simple backup/restore program'''
    Cluster.config_path = config

cli.add_command(backup)
cli.add_command(restore)
cli.add_command(stream)
cli.add_command(nagios)
