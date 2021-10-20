'''Test for rsync module'''

import pytest
import sysrsync
from unittest.mock import create_autospec
from unittest.mock import call, patch
from pathlib import Path

from backup.job.rsync import Rsync
from backup.backend.dummy import Dummy

@pytest.fixture(scope='function')
def jobfix(tmp_path):
    key = tmp_path / 'backup.key'
    key.write_text('')
    myjob = Rsync(
        hosts=['host01', 'host02', 'host03'],
        paths=[Path('/var/log')],
        run_style='seq',
        slotdir=Path('/BACKUP/MY_TEST/slots'),
        private_key=str(key),
        backend=Dummy(),
    )
    return key, myjob

class TestRsync:
    def test_create(self, jobfix):
        key, job = jobfix
        assert isinstance(job, Rsync)

    def test_backup(self, jobfix):
        key, job = jobfix
        patcher = patch('sysrsync.run')
        sysrsync_run = patcher.start()
        job.backup()
        sysrsync_run.assert_has_calls([
            call(source='/var/log', destination='/BACKUP/MY_TEST/slots/host01', source_ssh='host01', private_key=str(key), options=['-a']),
            call(source='/var/log', destination='/BACKUP/MY_TEST/slots/host02', source_ssh='host02', private_key=str(key), options=['-a']),
            call(source='/var/log', destination='/BACKUP/MY_TEST/slots/host03', source_ssh='host03', private_key=str(key), options=['-a']),
        ])
        patcher.stop()
