'''Test for Hashicorp Vault job'''

import os

import pytest
import responses
from pathlib import Path
from zipfile import ZipFile

from hazelsync.job.vault import Vault
from hazelsync.backend.dummy import Dummy

@pytest.fixture(scope='function')
def zipfixture():
    mydir = Path('tests/fixtures/vault')
    myzip = ZipFile
    with ZipFile('tests/fixtures/vault.snapshot', 'w') as myzip:
        for myfile in mydir.iterdir():
            myzip.write(str(myfile))
    return Path('tests/fixtures/vault.snapshot')

class TestVault:
    @responses.activate
    def test_backup(self, tmp_path, zipfixture):
        data = zipfixture.read_bytes()
        responses.add(responses.GET,
            'https://vault.example.com/v1/sys/storage/raft/snapshot',
            status=200, body=data)
        backend = Dummy(tmp_path)
        auth = {'method': 'token', 'token': 'dummy'}
        job = Vault('https://vault.example.com', auth, backend)
        slot = job.backup()[0]
        snap = slot / 'vault.snapshot'
        assert snap.is_file()
        assert snap.read_bytes() == data
