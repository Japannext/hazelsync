'''A tool to configure the SSH client and verify its configuration'''

from pathlib import Path

import click
import yaml

@click.command
def configure():
    '''Configure the SSH authorized key of a user'''
    pass

@click.command
def checkconfig():
    '''Check if the configuration provided is correct'''
    pass
