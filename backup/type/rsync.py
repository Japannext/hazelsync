'''Rsync style backup'''

from logging import getLogger
from enum import Enum
from pathlib import Path
from typing import List

import sysrsync
from sysrsync.exceptions import RsyncError

from ..utils import seq_run, async_run, convert_enum

log = getLogger(__name__)

class RunStyle(Enum):
    '''The run style of rsync (parallel or sequential)'''
    SEQ = 'seq'
    ASYNC = 'async'

class Rsync:
    '''A backup method to rsync data from a collection of hosts'''
    def __init__(self,
        hosts: List[str],
        paths: List[str],
        slotdir: str,
        private_key: str,
        run_style: str = 'seq',
    ):
        '''Create a new rsync plan.
        :param hosts: A list of hostnames to rsync to.
        :param paths: A list of path that will need to be rsynced from the target hosts.
        :param slotdir: A directory to use as a base for slots
        :param run_style: Whether to run the hosts sequentially or in parallel.
        '''
        self.hosts = hosts
        self.paths = [Path(path) for path in paths]
        self.slotdir = Path(slotdir)
        self.private_key = Path(private_key)
        run_style = RunStyle(run_style)
        functions = {
            RunStyle.SEQ: seq_run,
            RunStyle.ASYNC: async_run,
        }
        self.run_function = functions[run_style]
        self.status = []

    def backup(self):
        '''Run the job'''
        functions = []
        for host in self.hosts:
            functions.append((self.backup_rsync_host, [host]))
        self.run_function(functions)

    def backup_rsync_host(self, host: str):
        '''Rsync a single host
        :param host: The host to rsync.
        '''
        for path in self.paths:
            log.info("Running rsync on %s, %s", host, path)
            slot = self.slotdir / host
            try:
                cmd = sysrsync.command_maker.get_rsync_command(
                    source=str(path),
                    destination=str(slot),
                    source_ssh=host,
                    private_key=self.private_key,
                )
                log.debug("rsync command: %s", cmd)
                sysrsync.run(
                    source=str(path),
                    destination=str(slot),
                    source_ssh=host,
                    private_key=self.private_key,
                )
                self.status.append({'slot': slot, 'status': 'success'})
            except RsyncError as err:
                log.error("Rsync error for host=%s, path=%s: %s", host, path, err)
                self.status.append({'slot': slot, 'status': 'error', 'exception': err})
                continue

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