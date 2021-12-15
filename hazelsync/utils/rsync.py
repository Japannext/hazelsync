'''Utils for running rsync commands'''

import os
import subprocess #nosec
from logging import getLogger
from pathlib import Path
from typing import Optional, List

log = getLogger('hazelsync')

# Cronjob don't have PATH by default, so let's have sane defaults.
DEFAULT_PATH = ':'.join([
    '/bin',
    '/sbin',
    '/usr/bin',
    '/usr/local/bin',
    '/usr/local/sbin',
    '/usr/sbin',
])
# Do not change it with the default value of th get method.
# We need to use DEFAULT_PATH even when PATH return empty string.
PATH = os.environ.get('PATH') or DEFAULT_PATH

class RsyncError(RuntimeError):
    '''Error issued when the rsync command fails'''
    def __init__(self, err):
        super().__init__(f"Error during command `{err.cmd}` (return code {err.returncode}): {err.stderr}")

# pylint: disable=too-many-arguments
def rsync_run(
    source: Path,
    destination: Path,
    options: Optional[List[str]] = None,
    source_host: Optional[str] = None,
    dest_host: Optional[str] = None,
    includes: Optional[List[str]] = None,
    excludes: Optional[List[str]] = None,
    ssh_options: Optional[List[str]] = None,
    user: str = 'root',
    private_key: Optional[Path] = None,
):
    '''Run a sanitized rsync command'''
    if options is None:
        options = []
    if ssh_options is None:
        ssh_options = []
    source = f"{user}@{source_host}:{source}/" if source_host else f"{source}/"
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
    log.debug('Running command: %s', cmd)
    execute(cmd)

def execute(cmd):
    '''Execute a command and log properly'''
    try:
        proc = subprocess.run(cmd, shell=False, check=True, #nosec
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=dict(PATH=PATH))
        for line in proc.stdout.split(b'\n'):
            log.debug(line)
    except subprocess.CalledProcessError as err:
        raise Exception(f"Error during command `{err.cmd}` (return code {err.returncode}): {err.stderr}") from err
