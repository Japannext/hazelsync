'''Define the behavior of the SSH helper with the rsync plugin'''

from logging import getLogger
from pathlib import Path

from hazelsync.ssh import SshHelper, Unauthorized

log = getLogger('hazelsync')

class RsyncSsh(SshHelper):
    '''A class to handle the client authorization'''
    def __init__(self, config):
        self.allowed_scripts = config.get('allowed_scripts', [])
        self.allowed_paths = config.get('allowed_paths', [])
        log.debug("Allowed paths: %s", self.allowed_paths)
        log.debug("Allowed scripts: %s", self.allowed_scripts)

        if not isinstance(self.allowed_scripts, (tuple, list)):
            self.allowed_scripts = [self.allowed_scripts]
        if not isinstance(self.allowed_paths, (tuple, list)):
            self.allowed_paths = [self.allowed_paths]

        self.allowed_paths = list(map(Path, self.allowed_paths))

    def authorize(self, cmd_line: str):
        '''Return an exception if a command is unauthorized'''
        log.debug("Checking if `%s` is allowed", cmd_line)
        cmd = cmd_line.split(' ')

        if cmd_line in self.allowed_scripts:
            log.info("Command is in allowed scripts: `%s`", cmd_line)
            return

        if cmd[0] == 'rsync':
            log.debug("Rsync command. Will check path.")
            path_to_sync = Path(cmd[-1])
            for path in self.allowed_paths:
                log.debug("Checking if `%s` is among `%s`", path_to_sync, self.allowed_paths)
                if path_to_sync == path:
                    log.info("%s is in allowed path", path_to_sync)
                    return
                if path in path_to_sync.parents:
                    log.info("%s is in allowed path (children of %s)", path_to_sync, path)
                    return
            raise Unauthorized(f"Unauthorized backup path requested: {path_to_sync}")

        raise Unauthorized(f"Unauthorized command: {cmd_line}")
