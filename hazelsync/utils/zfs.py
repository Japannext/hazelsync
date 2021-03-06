'''
Utils for wrapping ZFS commands.
These utils exist due to the lack of support in the libzfs_core library.
'''

import subprocess #nosec
from pathlib import Path
from typing import Optional

from hazelsync.utils.rsync import PATH as _PATH

class ZfsError(RuntimeError):
    '''ZFS command runtime error'''

def _run(cmd):
    '''Run a command and wrap the errors'''
    try:
        proc = subprocess.run(cmd, #nosec
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            check=True,
            env=dict(PATH=_PATH))
    except subprocess.CalledProcessError as proc:
        stderr = proc.stderr
        cmd_line = ' '.join(cmd)
        exitcode = proc.returncode
        raise ZfsError(f"Failed to run `{cmd_line}` (exit {exitcode}): {stderr}") from proc
    return proc

def zfs_create(mount_point: Path):
    '''Create a dataset'''
    dataset = str(mount_point)[1:]
    cmd = ['zfs', 'create', dataset]
    _run(cmd)

def zfs_get(name: str, prop: str):
    '''Get a given property of an object'''
    cmd = ['/usr/bin/zfs', 'get', prop, name, '-H']
    proc = _run(cmd)
    line = proc.stdout.strip().split('\n')[0]
    _, _, value, _ = line.split('\t')
    return value

def zfs_set(name: str, prop: str, value: str):
    '''Set the properties of an object'''
    cmd = ['zfs', 'set', name, f"{prop}={value}"]
    prop = _run(cmd)

def zfs_ensure(name: str, prop: str, should: str):
    '''Ensure a property is set to a given value'''
    real = zfs_get(name, prop)
    if real != should:
        zfs_set(name, prop, should)

def zfs_list(dataset: Optional[str] = None):
    '''List the datasets available under a given path/name'''
    cmd = ['zfs', 'list', '-H', '-r', '-t', 'filesystem', str(dataset)]
    proc = _run(cmd)
    datasets = {}
    for line in proc.stdout.strip().split('\n'):
        name, used, avail, refer, mountpoint = line.split('\t')
        dataset = {'name': name, 'used': used, 'avail': avail, 'refer': refer}
        datasets[Path(mountpoint)] = dataset
    return datasets

def zfs_snapshot(mount_point: Path, properties: Optional[dict] = None):
    '''Create a snapshot for a dataset'''
    dataset = str(mount_point)[1:]
    property_list = []
    if properties:
        for key, value in properties.items():
            property_list += ['-o', f"{key}={value}"]
    cmd = ['zfs', 'snapshot', '-r', dataset, *property_list]
    _run(cmd)
