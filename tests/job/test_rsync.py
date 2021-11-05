'''Test for rsync module'''

import os
import pytest
from unittest.mock import create_autospec
from unittest.mock import call, patch
from pathlib import Path

from hazelsync.job.rsync import RsyncJob
from hazelsync.backend.dummy import DummyBackend
from hazelsync.utils.rsync import DEFAULT_PATH

@pytest.fixture(scope='function')
def backend(tmp_path):
    return DummyBackend(tmp_path)

@pytest.fixture(scope='function')
def private_key(tmp_path):
    key = tmp_path / 'backup.key'
    key.write_text('')
    return key

class TestRsync:
    def test_create(self, private_key, backend):
        job = RsyncJob(name='myhosts', hosts=['host01'], paths=['/var/log'], private_key=private_key, backend=backend)
        assert isinstance(job, RsyncJob)

    @patch('hazelsync.job.rsync.PATH', DEFAULT_PATH)
    def test_backup(self, private_key, backend):
        job = RsyncJob(name='myhosts', hosts=['host01', 'host02', 'host03'], paths=['/var/log'], private_key=private_key, backend=backend)
        with patch('hazelsync.job.rsync.rsync_run') as rsync:
            job.backup()
            options = ['-a', '-R', '-A', '--numeric-ids']
            args = {'source': Path('/var/log'), 'options': options, 'includes': None, 'excludes': None, 'private_key': private_key, 'user': 'root'}
            rsync.assert_has_calls([
                call(source_host='host01', destination=backend.tmp_dir/'host01', **args),
                call(source_host='host02', destination=backend.tmp_dir/'host02', **args),
                call(source_host='host03', destination=backend.tmp_dir/'host03', **args),
            ])

    @patch('hazelsync.job.rsync.PATH', DEFAULT_PATH)
    def test_pre_scripts(self, private_key, backend):
        job = RsyncJob(name='myhosts', hosts=['host01'], paths=['/var/log'],
            pre_scripts=['/usr/local/bin/my_custom_script arg1'], private_key=private_key, backend=backend)
        with patch('hazelsync.job.rsync.rsync_run'), patch('subprocess.run') as subprocess:
            job.backup()
            subprocess.assert_called_with(['ssh', '-l', 'root', '-i', str(private_key), 'host01', '/usr/local/bin/my_custom_script arg1'], check=True, shell=False, stderr=-1, stdout=-1, timeout=120, env=dict(PATH=DEFAULT_PATH))

    @patch('hazelsync.job.rsync.PATH', DEFAULT_PATH)
    def test_post_scripts(self, private_key, backend):
        job = RsyncJob(name='myhosts', hosts=['host01'], paths=['/var/log'],
            post_scripts=['/usr/local/bin/my_custom_script arg1'], private_key=private_key, backend=backend)
        with patch('hazelsync.job.rsync.rsync_run'), patch('subprocess.run') as subprocess:
            job.backup()
            subprocess.assert_called_with(['ssh', '-l', 'root', '-i', str(private_key), 'host01', '/usr/local/bin/my_custom_script arg1'], check=True, shell=False, stderr=-1, stdout=-1, timeout=120, env=dict(PATH=DEFAULT_PATH))

    def test_excludes(self, private_key, backend):
        job = RsyncJob(name='myhosts', hosts=['host01'], paths=['/var/log'],
            excludes=['/var/log/secure*', '/var/log/audit*'], private_key=private_key, backend=backend)
        with patch('hazelsync.job.rsync.rsync_run') as rsync:
            job.backup()
            options = ['-a', '-R', '-A', '--numeric-ids']
            args = {'source': Path('/var/log'), 'options': options, 'includes': None, 'excludes': ['/var/log/secure*', '/var/log/audit*'], 'private_key': private_key, 'user': 'root'}
            rsync.assert_called_with(source_host='host01', destination=backend.tmp_dir/'host01', **args)
