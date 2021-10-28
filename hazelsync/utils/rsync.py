'''Utils for running rsync commands'''

import shlex
import subprocess
from logging import getLogger
from pathlib import Path
from typing import Optional, List

log = getLogger(__name__)

class RsyncError(RuntimeError):
    def __init__(self, err):
        super().__init__(f"Error during command `{err.cmd}` (return code {err.returncode}): {err.stderr}")

def rsync_run(
    source: Path,
    destination: Path,
    options: Optional[List[str]] = None,
    source_host: Optional[str] = None,
    dest_host: Optional[str] = None,
    includes: Optional[List[str]] = None,
    excludes: Optional[List[str]] = None,
    ssh_options: Optional[List[str]] = None,
    private_key: Optional[Path] = None,
):
    '''Run a sanitized rsync command'''
    if options is None:
        options = []
    if ssh_options is None:
        ssh_options = []
    source = f"{source_host}:{source}/" if source_host else f"{source}/"
    destination = f"{dest_host}:{destination}/" if dest_host else f"{destination}/"
    if includes is not None:
        for inc in includes:
            options += ['--include', inc]
    if excludes is not None:
        for exc in excludes:
            options += ['--exclude', exc]
    if private_key:
        ssh_options += ['-i', str(private_key)]
    if ssh_options:
        ssh_string = 'ssh ' + ' '.join(ssh_options)
        options += ['--rsh', ssh_string]
    cmd = ['rsync', *options, source, destination]
    log.debug('Running command: %s', shlex.quote(' '.join(cmd)))
    execute(cmd)

def execute(cmd):
    '''Execute a command and log properly'''
    try:
        proc = subprocess.run(cmd, shell=False, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in proc.stdout.split(b'\n'):
            log.debug(line)
    except subprocess.CalledProcessError as err:
        raise Exception(f"Error during command `{err.cmd}` (return code {err.returncode}): {err.stderr}")
