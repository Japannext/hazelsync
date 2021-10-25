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
    slots = tmp_path / 'slots'
    slots.mkdir()
    key.write_text('')
    myjob = Rsync(
        name='myhosts',
        hosts=['host01', 'host02', 'host03'],
        paths=[Path('/var/log')],
        run_style='seq',
        basedir=Path(slots),
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
        with patch('sysrsync.run') as sysrsync:
            job.backup()
            slotdir = str(job.slotdir)
            sysrsync.assert_has_calls([
                call(source='/var/log', destination=f'{slotdir}/host01', source_ssh='host01', private_key=str(key), options=['-a']),
                call(source='/var/log', destination=f'{slotdir}/host02', source_ssh='host02', private_key=str(key), options=['-a']),
                call(source='/var/log', destination=f'{slotdir}/host03', source_ssh='host03', private_key=str(key), options=['-a']),
            ])

    def test_pre_scripts(self, jobfix):
        key, job = jobfix
        job.scripts['pre'] = ['/usr/local/bin/my_custom_script arg1']
        with patch('sysrsync.run') as sysrsync, patch('subprocess.run') as subprocess:
            job.backup()
            slotdir = str(job.slotdir)
            options = {'check': True, 'shell': False, 'stderr': -1, 'stdout': -1, 'timeout': 120}
            subprocess.assert_has_calls([
                call(['ssh', '-l', 'root', 'host01', '/usr/local/bin/my_custom_script arg1'], **options),
                call(['ssh', '-l', 'root', 'host02', '/usr/local/bin/my_custom_script arg1'], **options),
                call(['ssh', '-l', 'root', 'host03', '/usr/local/bin/my_custom_script arg1'], **options),
            ])

    def test_post_scripts(self, jobfix):
        key, job = jobfix
        job.scripts['post'] = ['/usr/local/bin/my_custom_script arg1']
        with patch('sysrsync.run') as sysrsync, patch('subprocess.run') as subprocess:
            job.backup()
            slotdir = str(job.slotdir)
            options = {'check': True, 'shell': False, 'stderr': -1, 'stdout': -1, 'timeout': 120}
            subprocess.assert_has_calls([
                call(['ssh', '-l', 'root', 'host01', '/usr/local/bin/my_custom_script arg1'], **options),
                call(['ssh', '-l', 'root', 'host02', '/usr/local/bin/my_custom_script arg1'], **options),
                call(['ssh', '-l', 'root', 'host03', '/usr/local/bin/my_custom_script arg1'], **options),
            ])
