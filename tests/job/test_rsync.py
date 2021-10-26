'''Test for rsync module'''

import pytest
from unittest.mock import create_autospec
from unittest.mock import call, patch
from pathlib import Path

from hazelsync.job.rsync import Rsync
from hazelsync.backend.dummy import Dummy

@pytest.fixture(scope='function')
def backend(tmp_path):
    return Dummy(tmp_path)

@pytest.fixture(scope='function')
def private_key(tmp_path):
    key = tmp_path / 'backup.key'
    key.write_text('')
    return str(key)

class TestRsync:
    def test_create(self, private_key, backend):
        job = Rsync(name='myhosts', hosts=['host01'], paths=['/var/log'], private_key=private_key, backend=backend)
        assert isinstance(job, Rsync)

    def test_backup(self, private_key, backend):
        job = Rsync(name='myhosts', hosts=['host01', 'host02', 'host03'], paths=['/var/log'], private_key=private_key, backend=backend)
        with patch('sysrsync.run') as sysrsync:
            job.backup()
            options = {'source': '/var/log', 'private_key': private_key, 'options': ['-a', '-R', '-A', '--numeric-ids']}
            sysrsync.assert_has_calls([
                call(destination=f'{backend.tmp_dir}/host01', source_ssh='host01', **options),
                call(destination=f'{backend.tmp_dir}/host02', source_ssh='host02', **options),
                call(destination=f'{backend.tmp_dir}/host03', source_ssh='host03', **options),
            ])

    def test_pre_scripts(self, private_key, backend):
        job = Rsync(name='myhosts', hosts=['host01'], paths=['/var/log'],
            pre_scripts=['/usr/local/bin/my_custom_script arg1'], private_key=private_key, backend=backend)
        with patch('sysrsync.run'), patch('subprocess.run') as subprocess:
            job.backup()
            subprocess.assert_called_with(['ssh', '-l', 'root', '-i', private_key, 'host01', '/usr/local/bin/my_custom_script arg1'],
                check=True, shell=False, stderr=-1, stdout=-1, timeout=120)

    def test_post_scripts(self, private_key, backend):
        job = Rsync(name='myhosts', hosts=['host01'], paths=['/var/log'],
            post_scripts=['/usr/local/bin/my_custom_script arg1'], private_key=private_key, backend=backend)
        with patch('sysrsync.run') as sysrsync, patch('subprocess.run') as subprocess:
            job.backup()
            subprocess.assert_called_with(['ssh', '-l', 'root', '-i', private_key, 'host01', '/usr/local/bin/my_custom_script arg1'],
                check=True, shell=False, stderr=-1, stdout=-1, timeout=120)

    def test_excludes(self, private_key, backend):
        job = Rsync(name='myhosts', hosts=['host01'], paths=['/var/log'],
            excludes=['/var/log/secure*', '/var/log/audit*'], private_key=private_key, backend=backend)
        with patch('sysrsync.run') as sysrsync:
            job.backup()
            rsync_options = ['-a', '-R', '-A', '--numeric-ids', '--exclude', '/var/log/secure*', '--exclude', '/var/log/audit*']
            sysrsync.assert_called_with(destination=f'{backend.tmp_dir}/host01',
                source_ssh='host01', source='/var/log', private_key=private_key, options=rsync_options)
