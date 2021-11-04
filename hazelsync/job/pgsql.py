'''Rsync style backup'''

from logging import getLogger
from pathlib import Path

from hazelsync.job.rsync import RsyncJob
from hazelsync.utils.rsync import rsync_run, RsyncError

log = getLogger(__name__)

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
        self.scripts['pre'] = ['''/usr/bin/psql -c "SELECT pg_backup_start('hazelsync', true);"''']
        self.scripts['final'] = ['''/usr/bin/psql -c "SELECT pg_backup_stop();"''']
        self.stream_options = []
        if delete_wal:
            self.stream_options += ['--remove-source-files']
        self.stream_timeout = stream_timeout

    def backup_rsync_host(self, host: str):
        try:
            super().backup_rsync_host(host)
        finally:
            self.run_scripts('final', host)

    def stream(self):
        '''A function to execute very regularly to avoid long backup time.
        In PostgreSQL case, we will rsync the WAL logs.
        '''
        for host in self.hosts:
            self.stream_host(host)

    def stream_host(self, host: str):
        '''Fetch the stream data for one host'''
        shortname = host.split('.')[0]
        slot = self.slots[shortname]
        with self.backend.lock(slot, self.stream_timeout):
            log.info("Running rsync (stream) on %s, %s", host, self.waldir)
            try:
                rsync_run(
                    source=self.waldir,
                    destination=slot,
                    source_host=host,
                    options=self.rsync_options+self.stream_options,
                    private_key=self.private_key,
                )
            except RsyncError as err:
                log.error("Failed to rsync (stream) for %s, %s: %s", host, self.waldir, err)
