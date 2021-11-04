'''Test for rsync module'''

import pytest
from unittest.mock import create_autospec
from unittest.mock import call, patch
from pathlib import Path

from hazelsync.job.pgsql import PgsqlJob
from hazelsync.backend.dummy import DummyBackend

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
        job = PgsqlJob(name='myhosts', hosts=['host01'], datadir='/data/pgsql', waldir='/data/wal', private_key=private_key, backend=backend)
        assert isinstance(job, PgsqlJob)

    def test_backup(self, private_key, backend):
        job = PgsqlJob(name='myhosts', hosts=['master01'], datadir='/data/pgsql', waldir='/data/wal', private_key=private_key, backend=backend)
        with patch('hazelsync.job.rsync.rsync_run') as rsync, \
        patch('subprocess.run') as subprocess:
            job.backup()
            options = ['-a', '-R', '-A', '--numeric-ids']
            args = {'source': Path('/data/pgsql'), 'options': options, 'includes': None, 'excludes': [Path('/data/wal')], 'private_key': private_key}
            rsync.assert_called_with(source_host='master01', destination=backend.tmp_dir/'master01', **args)
            backup_pre_script = '''/usr/bin/psql -c "SELECT pg_backup_start('hazelsync', true);"'''
            backup_post_script = '''/usr/bin/psql -c "SELECT pg_backup_stop();"'''
            print(subprocess.mock_calls)
            calls = [
                call(['ssh', '-l', 'root', '-i', str(private_key), 'master01', backup_pre_script], check=True, shell=False, stderr=-1, stdout=-1, timeout=120),
                call(['ssh', '-l', 'root', '-i', str(private_key), 'master01', backup_post_script], check=True, shell=False, stderr=-1, stdout=-1, timeout=120),
            ]
            assert subprocess.mock_calls == calls
            subprocess.assert_has_calls(calls)

    def test_stream(self, private_key, backend):
        job = PgsqlJob(name='myhosts', hosts=['master01'], datadir='/data/pgsql', waldir='/data/wal', private_key=private_key, backend=backend)
        with patch('hazelsync.job.pgsql.rsync_run') as rsync:
            job.stream()
            options = ['-a', '-R', '-A', '--numeric-ids', '--remove-source-files']
            args = {'source': Path('/data/wal'), 'options': options, 'private_key': private_key}
            rsync.assert_called_with(source_host='master01', destination=backend.tmp_dir/'master01', **args)
