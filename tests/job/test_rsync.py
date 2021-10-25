'''Test for rsync module'''

import pytest
from unittest.mock import create_autospec
from unittest.mock import call, patch
from pathlib import Path

from hazelsync.job.rsync import Rsync
from hazelsync.backend.dummy import Dummy

@pytest.fixture(scope='function')
def jobfix(tmp_path):
    key = tmp_path / 'backup.key'
    key.write_text('')
    myjob = Rsync(
        name='myhosts',
        hosts=['host01', 'host02', 'host03'],
        paths=[Path('/var/log')],
        run_style='seq',
        private_key=str(key),
        backend=Dummy(tmp_dir=tmp_path),
    )
    return key, myjob, tmp_path

class TestRsync:
    def test_create(self, jobfix):
        key, job, tmp_path = jobfix
        assert isinstance(job, Rsync)

    def test_backup(self, jobfix):
        key, job, tmp_path = jobfix
        with patch('sysrsync.run') as sysrsync:
            job.backup()
            options = {'source': '/var/log', 'private_key': str(key), 'options': ['-a', '-R', '-A', '--numeric-ids']}
            sysrsync.assert_has_calls([
                call(destination=f'{tmp_path}/host01', source_ssh='host01', **options),
                call(destination=f'{tmp_path}/host02', source_ssh='host02', **options),
                call(destination=f'{tmp_path}/host03', source_ssh='host03', **options),
            ])

    def test_pre_scripts(self, jobfix):
        key, job, tmp_path = jobfix
        job.scripts['pre'] = ['/usr/local/bin/my_custom_script arg1']
        with patch('sysrsync.run') as sysrsync, patch('subprocess.run') as subprocess:
            job.backup()
            options = {'check': True, 'shell': False, 'stderr': -1, 'stdout': -1, 'timeout': 120}
            subprocess.assert_has_calls([
                call(['ssh', '-l', 'root', 'host01', '/usr/local/bin/my_custom_script arg1'], **options),
                call(['ssh', '-l', 'root', 'host02', '/usr/local/bin/my_custom_script arg1'], **options),
                call(['ssh', '-l', 'root', 'host03', '/usr/local/bin/my_custom_script arg1'], **options),
            ])

    def test_post_scripts(self, jobfix):
        key, job, tmp_path = jobfix
        job.scripts['post'] = ['/usr/local/bin/my_custom_script arg1']
        with patch('sysrsync.run') as sysrsync, patch('subprocess.run') as subprocess:
            job.backup()
            options = {'check': True, 'shell': False, 'stderr': -1, 'stdout': -1, 'timeout': 120}
            subprocess.assert_has_calls([
                call(['ssh', '-l', 'root', 'host01', '/usr/local/bin/my_custom_script arg1'], **options),
                call(['ssh', '-l', 'root', 'host02', '/usr/local/bin/my_custom_script arg1'], **options),
                call(['ssh', '-l', 'root', 'host03', '/usr/local/bin/my_custom_script arg1'], **options),
            ])
