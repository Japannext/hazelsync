'''Rsync style backup'''

import subprocess
from logging import getLogger
from enum import Enum
from pathlib import Path
from typing import List, Union, Optional

from hazelsync.utils.rsync import rsync_run, RsyncError, PATH

Script = Union[str, dict]

log = getLogger(__name__)

class RunStyle(Enum):
    '''The run style of rsync (parallel or sequential)'''
    SEQ = 'seq'
    ASYNC = 'async'

class RsyncJob:
    '''A backup method to rsync data from a collection of hosts'''
    def __init__(self,
        name: str,
        hosts: List[str],
        paths: List[str],
        private_key: str,
        backend,
        user: str = 'root',
        includes: Optional[List[str]] = None,
        excludes: Optional[List[str]] = None,
        pre_scripts: Optional[List[Script]] = None,
        post_scripts: Optional[List[Script]] = None,
        run_style: str = 'seq',
    ):
        '''Create a new rsync plan.
        :param hosts: A list of hostnames to rsync to.
        :param paths: A list of path that will need to be rsynced from the target hosts.
        :param run_style: Whether to run the hosts sequentially or in parallel.
        '''
        self.hosts = hosts
        self.paths = [Path(path) for path in paths]
        self.private_key = Path(private_key)
        self.run_style = RunStyle(run_style)
        self.status = []
        self.backend = backend
        self.user = user
        self.scripts = {}
        self.scripts['pre'] = pre_scripts or []
        self.scripts['post'] = post_scripts or []
        self.rsync_options = ['-a', '-R', '-A', '--numeric-ids']
        self.includes = includes
        self.excludes = excludes

        self.slots = {host.split('.')[0]: self.backend.ensure_slot(host.split('.')[0]) for host in self.hosts}

    def backup(self):
        '''Run the job'''
        slots = []
        if self.run_style == RunStyle.SEQ:
            for host in self.hosts:
                try:
                    slot = self.backup_rsync_host(host)
                    slots.append(slot)
                except Exception as err:
                    log.error(err)
                    continue
        elif self.run_style == RunStyle.ASYNC:
            raise NotImplementedError()
        return slots

    def run_scripts(self, stype: str, host: str):
        '''Run a collection of scripts on a given host'''
        for script in self.scripts[stype]:
            if isinstance(script, str):
                data = {'cmd': script}
            elif isinstance(script, dict):
                data = script
            script_cmd = data['cmd']
            timeout = data.get('timeout', 120)
            log.debug("Running %s script: %s", stype, script_cmd)
            cmd = ['ssh', '-l', self.user, '-i', str(self.private_key), host, script_cmd]
            subprocess.run(cmd, shell=False, timeout=timeout, env=dict(PATH=PATH),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    def backup_rsync_host(self, host: str):
        '''Rsync a single host
        :param host: The host to rsync.
        '''
        shortname = host.split('.')[0]
        slot = self.slots[shortname]
        with self.backend.lock(slot):
            self.run_scripts('pre', host)
            for path in self.paths:
                log.info("Running rsync on %s, %s", host, path)
                try:
                    rsync_run(
                        source=path,
                        destination=slot,
                        source_host=host,
                        options=self.rsync_options,
                        includes=self.includes,
                        excludes=self.excludes,
                        user=self.user,
                        private_key=self.private_key,
                    )
                    self.status.append({'slot': slot, 'status': 'success'})
                except RsyncError as err:
                    self.status.append({'slot': slot, 'status': 'error', 'exception': err})
                    continue
        errors = [s for s in self.status if s['status'] == 'error']
        if errors:
            errors_str = ', '.join(map(lambda s: f"{s['slot']}: {s['exception']}", errors))
            raise Exception(errors_str)
        self.run_scripts('post', host)
        return slot

    def restore(self):
        '''Restore job
        '''
        raise NotImplementedError()

    def restore_rsync_host(self, host: str, snapshot: Path):
        '''Restore the data of a single host
        :param host: The host to restore
        :param snapshot: The snapshot to restore
        '''
        raise NotImplementedError()
