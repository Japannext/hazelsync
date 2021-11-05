'''Test rsync SSH helper'''

import pytest

from hazelsync.ssh import Unauthorized
from hazelsync.ssh.pgsql import PgsqlSsh

def test_authorize_allow():
    cmd_line = 'rsync --server --sender -logDtpArRe.iLsfxC --numeric-ids . /opt/data'
    helper = PgsqlSsh(dict(allowed_paths=['/opt/data']))
    helper.authorize(cmd_line)

def test_authorize_reject():
    cmd_line = 'rsync --server --sender -logDtpArRe.iLsfxC --numeric-ids . /opt/data1'
    helper = PgsqlSsh(dict(allowed_paths=['/opt/data']))
    with pytest.raises(Unauthorized):
        helper.authorize(cmd_line)

def test_authorize_string_path():
    cmd_line = 'rsync --server --sender -logDtpArRe.iLsfxC --numeric-ids . /opt/data'
    helper = PgsqlSsh(dict(allowed_paths='/opt/data'))
    helper.authorize(cmd_line)

def test_authorize_prescript_allow():
    cmd_line = '''psql -c "SELECT pg_start_backup('hazelsync', true);"'''
    helper = PgsqlSsh(dict(allowed_paths='/opt/data'))
    helper.authorize(cmd_line)

def test_authorize_script_reject():
    cmd_line = '''psql -c "DROP DATABASE postgres;"'''
    helper = PgsqlSsh(dict(allowed_paths='/opt/data'))
    with pytest.raises(Unauthorized):
        helper.authorize(cmd_line)

def test_authorize_postscript_allow():
    cmd_line = '''psql -c "SELECT pg_stop_backup();"'''
    helper = PgsqlSsh(dict(allowed_paths='/opt/data'))
    helper.authorize(cmd_line)
