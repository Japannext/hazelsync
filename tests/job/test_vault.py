'''Test for Hashicorp Vault job'''

import os
import responses

from hazelsync.job.vault import Vault
from hazelsync.backend.dummy import Dummy

class TestVault:
    @responses.activate
    def test_backup(self, tmp_path):
        data = os.urandom(1024*1024)
        responses.add(responses.GET,
            'https://vault.example.com/v1/sys/storage/raft/snapshot',
            status=200, body=data)
        backend = Dummy(tmp_path)
        auth = {'method': 'token', 'token': 'dummy'}
        job = Vault('https://vault.example.com', auth, backend)
        job.backup()
        assert job.slot.is_file()
        assert job.slot.read_bytes() == data
