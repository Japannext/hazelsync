'''A job to backup hashicorp Vault'''

from gzip import GzipFile
from logging import getLogger
from pathlib import Path
from urllib.parse import urlparse

import hvac
import requests

from hazelsync.utils.functions import ca_bundle

CHUNK_SIZE = 1024*1024 # 1MB

log = getLogger('hazelsync')

def verify_gzip(path: Path):
    '''Verify the CRC of a gzip
    :param path: Path to the gzip to verify
    :raises BadGzipFile: Will raise this exception if the gzip is invalid
    '''
    GzipFile(str(path)).read()

class VaultJob:
    '''A job to backup and restore Hashicorp Vault'''
    def __init__(self,
        name: str,
        url: str,
        auth: dict,
        backend,
        ca: str = ca_bundle(),
    ):
        self.name = name
        uri = urlparse(url)
        self.client = hvac.Client(url)
        if ca:
            session = requests.Session()
            self.client.session = session
            session.verify = ca
        method = auth.pop('method')
        self.login(method, auth)

        self.slot = backend.ensure_slot(uri.hostname)
        self.lock = backend.lock(self.slot)

    def login(self, auth_method: str, options: dict):
        '''Login a HVAC client with the given authentication method'''
        if auth_method == 'token':
            self.client.token = options.get('token')
        elif auth_method == 'tls':
            pass
        else:
            try:
                getattr(self.client.auth, auth_method).login(**options)
            except AttributeError as err:
                log.error("Auth method %s not supported by python hvac library", auth_method)
                raise err

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
        raise NotImplementedError("Restore for Hashicorp Vault not implemented yet")
