'''
A script that execute on the client to restrict the backup server access rights
to improve security.
Upon accessing the client through SSH, the SSH_ORIGINAL_COMMAND will be inspected
and depending on the local configuration in /etc/backup-client.yaml, the command
will be accepted or rejected.
'''

import os
import subprocess #nosec
import sys
from logging import getLogger
from logging.handlers import SysLogHandler
from pathlib import Path

import click
import yaml

from hazelsync import Plugin
from hazelsync.ssh_helper import Authorized, Unauthorized

log = getLogger('hazel-ssh-helper')
log.addHandler(SysLogHandler(address='/dev/log'))

CONFIG_FILE = Path('/etc/hazelsync-ssh-helper.yaml')

@click.command()
def ssh_helper():
    '''A ssh client command to restrict the rights of the backup server'''
    try:
        cmd_line = os.environ.get('SSH_ORIGINAL_COMMAND', '')
        log.debug("Receiving command: %s", cmd_line)
        config = yaml.safe_load(CONFIG_FILE.read_text(encoding='utf-8'))
        plugin_name = config.get('plugin')

        plugin_config = config.get(plugin_name, {})
        plugin = Plugin('ssh_helper').get(plugin_name)(**plugin_config)

        if getattr(plugin, 'run'):
            plugin.run(cmd_line)

        elif getattr(plugin, 'authorize'):
            plugin.authorize(cmd_line)
            subprocess.run(cmd_line, check=True, shell=True) #nosec

    except Unauthorized as err:
        log.error("Unauthorized: %s", err)
        sys.exit(1)
    except subprocess.CalledProcessError as err:
        log.error("Failed to run command %s: %s", err.cmd, err.stderr)
