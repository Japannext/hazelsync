'''A job to backup hashicorp Vault'''

from zipfile import ZipFile
from urllib.parse import urlparse
from logging import getLogger

import hvac
import requests

from hazelsync.backend import Backend
from hazelsync.utils.functions import ca_bundle

CHUNK_SIZE = 1024*1024 # 1MB

log = getLogger(__name__)

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

class Vault:
    '''A job to backup and restore Hashicorp Vault'''
    def __init__(self,
        url: str,
        auth: dict,
        backend: Backend,
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

    def verify(self):
        '''Verify the integrity o the data downloaded'''
        snapshot_file = str(self.slot / 'vault.snapshot')
        with ZipFile(snapshot_file) as myzip:
            result = myzip.testzip()
            if result is None:
                log.info(f"Could verify CRC code for snapshot {snapshot_file}")
            else:
                raise Exception(f"Could not verify snapshot CRC code: {result} is corrupt")

    def backup(self):
        '''Backup Hashicorp Vault with the REST API'''
        resp = self.client.sys.take_raft_snapshot()
        resp.raise_for_status()
        snapshot_file = self.slot / 'vault.snapshot'
        with snapshot_file.open('wb+') as myfile:
            for chunk in resp.iter_content(CHUNK_SIZE, decode_unicode=False):
                if chunk:
                    myfile.write(chunk)
        resp.close()
        self.verify()
        return [self.slot]

    def restore(self, snapshot):
        '''Restore Hashicorp Vault with the REST API'''
        pass

JOB = Vault
