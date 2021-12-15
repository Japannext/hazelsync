'''Define the behavior of the SSH helper with the rsync plugin'''

from logging import getLogger

from hazelsync.ssh.rsync import RsyncSsh
from hazelsync.job.pgsql import PRE_SCRIPT, POST_SCRIPT

log = getLogger('hazelsync')

class PgsqlSsh(RsyncSsh):
    '''A class to handle the client authorization'''
    def __init__(self, config):
        super().__init__(config)
        self.allowed_scripts = [PRE_SCRIPT, POST_SCRIPT]
