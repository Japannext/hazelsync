'''Test rsync SSH helper'''

import pytest

from hazelsync.ssh import Unauthorized
from hazelsync.ssh.rsync import RsyncSsh

def test_authorize_allow():
    cmd_line = 'rsync --server --sender -logDtpArRe.iLsfxC --numeric-ids . /opt/data'
    helper = RsyncSsh(dict(allowed_paths=['/opt/data']))
    helper.authorize(cmd_line)

def test_authorize_reject():
    cmd_line = 'rsync --server --sender -logDtpArRe.iLsfxC --numeric-ids . /opt/data1'
    helper = RsyncSsh(dict(allowed_paths=['/opt/data']))
    with pytest.raises(Unauthorized):
        helper.authorize(cmd_line)

def test_authorize_string_path():
    cmd_line = 'rsync --server --sender -logDtpArRe.iLsfxC --numeric-ids . /opt/data'
    helper = RsyncSsh(dict(allowed_paths='/opt/data'))
    helper.authorize(cmd_line)
