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

log = getLogger('hazel-ssh')
log.addHandler(SysLogHandler(address='/dev/log'))

CONFIG_FILE = Path('/etc/hazelsync-ssh.yaml')

class Unauthorized(RuntimeError):
    '''An exception to reject unauthorized commands'''

@click.command()
def ssh():
    '''A ssh client command to restrict the rights of the backup server'''
    try:
        cmd_line = os.environ.get('SSH_ORIGINAL_COMMAND', '')
        cmd = cmd_line.split(' ')
        log.debug("Receiving command: %s", ' '.join(cmd))
        config = yaml.safe_load(CONFIG_FILE.read_text())
        allowed_scripts = config.get('allowed_scripts', [])
        allowed_paths = config.get('allowed_paths', [])

        if len(cmd) == 0:
            raise Exception("No command provided in SSH_ORIGINAL_COMMAND")
        if cmd_line in allowed_scripts:
            log.info("Running authorized command: %s", cmd_line)
            proc = subprocess.run(cmd, check=True) #nosec
        elif cmd[0] == 'rsync':
            path_to_sync = Path(cmd[-1])
            for path in allowed_paths:
                path = Path(path)
                if path_to_sync == path or path_to_sync in path.parents:
                    proc = subprocess.run(cmd, check=True) #nosec
                    break
            else:
                raise Unauthorized(f"Unauthorized backup path requested: {path_to_sync}")
        else:
            raise Unauthorized(f"Unauthorized command: {cmd_line}")
    except subprocess.CalledProcessError as err:
        log.error(err)
        sys.exit(proc.returncode)
    except Exception as err:
        log.error(err)
        sys.exit(1)
