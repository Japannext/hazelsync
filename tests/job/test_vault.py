'''Test for Hashicorp Vault job'''

import os

import pytest
import responses
from pathlib import Path

from hazelsync.job.vault import Vault
from hazelsync.backend.dummy import Dummy

@pytest.fixture(scope='function')
def zipfixture():
    path = 'tests/fixtures/vault.snapshot'
    return Path(path)

class TestVault:
    @responses.activate
    def test_backup(self, tmp_path, zipfixture):
        data = zipfixture.read_bytes()
        responses.add(responses.GET,
            'https://vault.example.com/v1/sys/storage/raft/snapshot',
            status=200, body=data)
        backend = Dummy(tmp_path)
        auth = {'method': 'token', 'token': 'dummy'}
        job = Vault('vault', 'https://vault.example.com', auth, backend)
        slot = job.backup()[0]
        snap = slot / 'vault.snapshot'
        assert snap.is_file()
        assert snap.read_bytes() == data
