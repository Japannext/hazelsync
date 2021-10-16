'''Test for rsync module'''

import pytest
import sysrsync
from unittest.mock import create_autospec
from unittest.mock import call, patch
from pathlib import Path

from backup.type.rsync import Rsync

@pytest.fixture(scope='function')
def job():
    job = Rsync(
        hosts=['host01', 'host02', 'host03'],
        paths=[Path('/var/log')],
        run_style='seq',
        slotdir=Path('/BACKUP/MY_TEST/slots'),
    )
    return job

class TestRsync:
    def test_create(self, job):
        assert isinstance(job, Rsync)

    def test_backup(self, job):
        #sysrsync_run = create_autospec(sysrsync.run)
        patcher = patch('sysrsync.run')
        sysrsync_run = patcher.start()
        job.backup()
        sysrsync_run.assert_has_calls([
            call(source='/var/log', destination='/BACKUP/MY_TEST/slots/host01', source_ssh='host01'),
            call(source='/var/log', destination='/BACKUP/MY_TEST/slots/host02', source_ssh='host02'),
            call(source='/var/log', destination='/BACKUP/MY_TEST/slots/host03', source_ssh='host03'),
        ])
        patcher.stop()
