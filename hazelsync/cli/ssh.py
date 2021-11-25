'''
A script that execute on the client to restrict the backup server access rights
to improve security.
Upon accessing the client through SSH, the SSH_ORIGINAL_COMMAND will be inspected
and depending on the local configuration in /etc/hazelsync-ssh.yaml, the command
will be accepted or rejected.
'''

import os
import subprocess #nosec
import sys
import logging
from logging import getLogger
from logging.handlers import SysLogHandler
from pathlib import Path

import click
import click_logging
import yaml

from hazelsync.plugin import Plugin
from hazelsync.ssh import Unauthorized

log = getLogger('hazelsync')
#log.addHandler(SysLogHandler(address='/dev/log'))
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
click_logging.basic_config(log)

CONFIG_FILE = '/etc/hazelsync-ssh.yaml'

def get_config(path: Path) -> dict:
    '''Fetch the configuration file'''
    return yaml.safe_load(path.read_text(encoding='utf-8'))

@click.command()
@click.option('--config', '-c', default=CONFIG_FILE, help='The config file to use.', show_default=True)
def ssh(config):
    '''A ssh client command to restrict the rights of the backup server'''
    try:
        cmd_line = os.environ.get('SSH_ORIGINAL_COMMAND', '')
        log.debug("Receiving command: %s", cmd_line)
        config = get_config(Path(config))
        log.debug("Loading SSH helper plugin")
        plugin_name = config.get('plugin')
        plugin_config = config.get('options', {})

        log.debug("Initializing SSH helper plugin")
        plugin = Plugin('ssh').get(plugin_name)
        log.debug("Loaded plugin %s", plugin)
        helper = plugin(plugin_config)

        log.debug("Running SSH helper plugin")
        helper.run(cmd_line)

    except Unauthorized as err:
        log.error("Unauthorized: %s", err)
        sys.exit(1)
