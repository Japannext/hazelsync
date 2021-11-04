'''Define the behavior of the SSH helper with the rsync plugin'''

import subprocess
from logging import getLogger
from pathlib import Path

from hazelsync.ssh import SshHelper, Unauthorized
from hazelsync.ssh

log = getLogger(__name__)

class RsyncSsh(SshHelper):
    '''A class to handle the client authorization'''
    def __init__(self, config):
        self.allowed_scripts = config.get('allowed_scripts', [])
        self.allowed_paths = config.get('allowed_paths', [])

    def authorize(self, cmd_line: str):
        '''Return an exception if a command is unauthorized'''
        cmd = cmd_line.split(' ')

        if cmd_line in self.allowed_scripts:
            log.info("Running authorized command: %s", cmd_line)
            proc = subprocess.run(cmd, check=True) #nosec

        elif Path(cmd[0]).name == 'rsync':
            path_to_sync = Path(cmd[-1])
            for path in self.allowed_paths:
                path = Path(path)
                if path_to_sync == path or path_to_sync in path.parents:
                    proc = subprocess.run(cmd, check=True) #nosec
                    break
            else:
                raise Unauthorized(f"Unauthorized backup path requested: {path_to_sync}")
        else:
            raise Unauthorized(f"Unauthorized command: {cmd_line}")
