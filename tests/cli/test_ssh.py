'''Testing hazel-ssh CLI'''

import logging
import pytest
from unittest.mock import patch
from logging import getLogger
import traceback

from click.testing import CliRunner

from hazelsync.cli.ssh import ssh
from hazelsync.ssh import Unauthorized

log = getLogger('hazelsync')

@patch('subprocess.run')
@patch('hazelsync.cli.ssh.get_config', lambda x: {'plugin': 'rsync', 'options': {'allowed_paths': ['/opt/data']}})
def test_ssh_allow(subprocess, caplog):
    caplog.set_level(logging.DEBUG)
    runner = CliRunner(mix_stderr=True)
    cmd = 'rsync --server --sender -logDtpArRe.iLsfxC --numeric-ids . /opt/data'
    result = runner.invoke(ssh, env=dict(SSH_ORIGINAL_COMMAND=cmd))
    if result.exception:
        log.error(result.exception)
        log.exception(result.exception)
        traceback.print_tb(result.exception.__traceback__)
    assert result.exit_code == 0

@patch('subprocess.run')
@patch('hazelsync.cli.ssh.get_config', lambda x: {'plugin': 'rsync', 'options': {'allowed_paths': ['/opt/data1']}})
def test_ssh_deny(subprocess):
    runner = CliRunner(mix_stderr=True)
    cmd = 'rsync --server --sender -logDtpArRe.iLsfxC --numeric-ids . /opt/data2'
    result = runner.invoke(ssh, env=dict(SSH_ORIGINAL_COMMAND=cmd))
    if result.exception:
        log.error(result.exception)
    assert result.exit_code == 1

@patch('subprocess.run')
@patch('hazelsync.cli.ssh.get_config', lambda x: {'plugin': 'pgsql', 'options': {'allowed_paths': ['/opt/data']}})
def test_ssh_pgsql_allow(subprocess):
    runner = CliRunner(mix_stderr=True)
    cmd = 'rsync --server --sender -logDtpArRe.iLsfxC --numeric-ids . /opt/data'
    result = runner.invoke(ssh, env=dict(SSH_ORIGINAL_COMMAND=cmd))
    if result.exception:
        log.error(result.exception)
    assert result.exit_code == 0
