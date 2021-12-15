'''Rsync style backup'''

from logging import getLogger
from pathlib import Path

from filelock import Timeout

from hazelsync.job.rsync import RsyncJob
from hazelsync.utils.rsync import rsync_run, RsyncError

log = getLogger('hazelsync')

PRE_SCRIPT = '''psql -c "SELECT pg_start_backup('hazelsync', true);"'''
POST_SCRIPT = '''psql -c "SELECT pg_stop_backup();"'''

class PgsqlJob(RsyncJob):
    '''Subclass of rsync job to backup PostgreSQL with the WAL archive method.'''
    def __init__(self,
        datadir: str,
        waldir: str,
        delete_wal: bool = True,
        stream_timeout: int = 60,
        **kwargs):
        self.waldir = Path(waldir)
        super().__init__(paths=[Path(datadir)], excludes=[self.waldir], **kwargs)
        self.scripts['pre'] = [PRE_SCRIPT]
        self.scripts['final'] = [POST_SCRIPT]
        self.stream_options = []
        if delete_wal:
            self.stream_options += ['--remove-source-files']
        self.stream_timeout = stream_timeout

    def backup_rsync_host(self, host: str):
        try:
            return super().backup_rsync_host(host)
        finally:
            self.run_scripts('final', host)

    def stream(self):
        '''A function to execute very regularly to avoid long backup time.
        In PostgreSQL case, we will rsync the WAL logs.
        '''
        slots = []
        for host in self.hosts:
            slot = {'slot': host.split('.')[0]}
            try:
                self.stream_host(host)
                slot['status'] = 'success'
            except RsyncError as err:
                log.error("Failed to rsync (stream) for %s, %s: %s", host, self.waldir, err)
                slot['status'] = 'failure'
                slot['logs'] = str(err)
            except Timeout:
                slot['status'] = 'locked'
            except Exception as err:
                slot['status'] = 'unknown'
                slot['logs'] = str(err)
            slots.append(slot)
        return slots

    def stream_host(self, host: str):
        '''Fetch the stream data for one host'''
        shortname = host.split('.')[0]
        slot = self.slots[shortname]
        with self.backend.lock(slot, self.stream_timeout):
            log.info("Running rsync (stream) on %s, %s", host, self.waldir)
            rsync_run(
                source=self.waldir,
                destination=slot,
                source_host=host,
                options=self.rsync_options+self.stream_options,
                user=self.user,
                private_key=self.private_key,
            )

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
