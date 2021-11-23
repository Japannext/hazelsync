'''Test for checking nagios output'''

from textwrap import dedent
from logging import getLogger

import traceback
import logging
import pytest
import yaml
from click.testing import CliRunner
from freezegun import freeze_time

from hazelsync.cli.nagios import nagios, merge_status
from hazelsync.settings import Settings

GLOBALS = '''\
default_backend: zfs
job_options:
  rsync:
    user: root
    private_key: /etc/hazelsync.key
backend_options:
  zfs:
    basedir: /backup
'''

BACKUPS = {
    'backup1': dedent('''\
        job: rsync
        options:
            hosts: [host01, host02, host03]
            paths: ['/opt/backup']
    '''),
}

REPORTS = {
    'backup1': {
        '2020-12-24T01:00:00': dedent('''\
        cluster: backup1
        job_type: backup
        job_name: rsync
        start_time: '2020-12-24T01:00:00'
        end_time: '2020-12-24T02:00:00'
        status: success
        slots:
        - {slot: '/opt/backup', status: 'success'}
        ''')
    }
}

log = getLogger(__name__)

@pytest.fixture(scope='function')
def dirs(tmp_path):

    backups = BACKUPS
    reports = REPORTS

    globals = tmp_path / 'globals.yaml'
    Settings.globals = globals

    globals.write_text(GLOBALS)

    clusterdir = tmp_path / 'clusters'
    clusterdir.mkdir()
    for name, backup in backups.items():
        filename = clusterdir / f"{name}.yaml"
        filename.write_text(backup)

    reportdir = tmp_path / 'reports'
    reportdir.mkdir()
    for name, reports in reports.items():
        for report_name, report in reports.items():
            filename = reportdir / name / f"{report_name}.yaml"
            filename.parent.mkdir(parents=True, exist_ok=True)
            filename.write_text(report)

    return (clusterdir, reportdir)

@freeze_time('2020-12-24T12:00:00+09:00')
def test_nagios(dirs, caplog):
    clusterdir, reportdir = dirs
    caplog.set_level(logging.DEBUG)
    runner = CliRunner(mix_stderr=True)
    result = runner.invoke(nagios, ['--clusterdir', str(clusterdir), '--reportdir', str(reportdir)])
    if result.exception:
        log.error(result.exception)
        log.exception(result.exception)
        traceback.print_tb(result.exception.__traceback__)
    assert result.exit_code == 0
    assert result.output == dedent('''\
        OK Hazelsync backups - 1/1
        [OK] backup1 Slots: 1/1 succeeded
    ''')

def test_merge_status():
    assert merge_status('ok', 'unknown') == 'unknown'
    assert merge_status('ok', 'ok') == 'ok'
    assert merge_status('unknown', 'critical') == 'critical'
    assert merge_status('warning', 'unknown') == 'unknown'
