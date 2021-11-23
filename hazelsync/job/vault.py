'''A job to backup hashicorp Vault'''

from urllib.parse import urlparse
from logging import getLogger
from gzip import GzipFile

import hvac
import requests
from pathlib import Path

from hazelsync.utils.functions import ca_bundle

CHUNK_SIZE = 1024*1024 # 1MB

log = getLogger(__name__)

def verify_gzip(path: Path):
    '''Verify the CRC of a gzip
    :param path: Path to the gzip to verify
    :raises BadGzipFile: Will raise this exception if the gzip is invalid
    '''
    GzipFile(str(path)).read()

class AuthMethod:
    '''A valid authentication method with its parameters'''
    def __init__(self, method, **kwargs):
        self.method = method
        self.kwargs = kwargs
    def login(self, client):
        '''Login a HVAC client with the given authentication method'''
        if self.method == 'token':
            client.token = self.kwargs.get('token')
        elif self.method == 'tls':
            pass
        else:
            try:
                getattr(client.auth, self.method).login(**self.kwargs)
            except AttributeError as err:
                log.error("Auth method %s not supported by python hvac library", self.method)
                raise err

class VaultJob:
    '''A job to backup and restore Hashicorp Vault'''
    def __init__(self,
        name: str,
        url: str,
        auth: dict,
        backend,
        ca: str = ca_bundle(),
    ):
        uri = urlparse(url)
        self.client = hvac.Client(url)
        if ca:
            session = requests.Session()
            self.client.session = session
            session.verify = ca
        method = auth.pop('method')
        auth_method = AuthMethod(method, **auth)
        auth_method.login(self.client)

        self.slot = backend.ensure_slot(uri.hostname)
        self.lock = backend.lock(self.slot)

    def backup(self):
        '''Backup Hashicorp Vault with the REST API'''
        with self.lock:
            try:
                slot = {'slot': self.slot}
                snapshot_file = self.slot / 'vault.snapshot'
                resp = self.client.sys.take_raft_snapshot()
                resp.raise_for_status()
                with snapshot_file.open('wb+') as myfile:
                    for chunk in resp.iter_content(CHUNK_SIZE, decode_unicode=False):
                        if chunk:
                            myfile.write(chunk)
                resp.close()
                verify_gzip(snapshot_file)
                slot['status'] = 'success'
            except Exception as err:
                log.error(err)
                slot['status'] = 'failure'
            return [slot]

    def restore(self, snapshot):
        '''Restore Hashicorp Vault with the REST API'''
        pass
