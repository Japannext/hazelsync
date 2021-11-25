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
from hazelsync.settings import ClusterSettings


class TestNagios:
    clusters = {
        'backup1': {
            'job': 'rsync',
            'options': {
                'hosts': ['host01', 'host02', 'host03'],
                'paths': ['/opt/backup'],
            },
        },
    }
    reports = {
        'backup1': {
            '2020-12-24T01:00:00': {
                'cluster': 'backup1',
                'job_type': 'backup',
                'job_name': 'rsync',
                'start_time': '2020-12-24T01:00:00',
                'end_time': '2020-12-24T02:00:00',
                'status': 'success',
                'slots': [{'slot': '/opt/backup', 'status': 'success'}],
            }
        }
    }

    @freeze_time('2020-12-24T12:00:00+09:00')
    def test_nagios(self, clusterdir, reportdir, caplog):
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

    def test_merge_status(self):
        assert merge_status('ok', 'unknown') == 'unknown'
        assert merge_status('ok', 'ok') == 'ok'
        assert merge_status('unknown', 'critical') == 'critical'
        assert merge_status('warning', 'unknown') == 'unknown'
