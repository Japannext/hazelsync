'''Test for Hashicorp Vault job'''

import os

import pytest
import responses
from pathlib import Path

from hazelsync.job.vault import VaultJob
from hazelsync.backend.dummy import DummyBackend

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
        backend = DummyBackend(tmp_path)
        auth = {'method': 'token', 'token': 'dummy'}
        job = VaultJob('vault', 'https://vault.example.com', auth, backend)
        slot = job.backup()[0]['slot']
        snap = slot / 'vault.snapshot'
        assert snap.is_file()
        assert snap.read_bytes() == data
