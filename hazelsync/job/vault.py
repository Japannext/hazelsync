'''A job to backup hashicorp Vault'''

from urllib.parse import urlparse
from logging import getLogger

import hvac

from hazelsync.backend import Backend

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
    ):
        uri = urlparse(url)
        self.client = hvac.Client(url)
        method = auth.pop('method')
        auth_method = AuthMethod(method, **auth)
        auth_method.login(self.client)

        self.slot = backend.ensure_slot(uri.hostname)

    def backup(self):
        '''Backup Hashicorp Vault with the REST API'''
        stream = self.client.sys.take_raft_snapshot()
        stream.raise_for_status()
        with self.slot.open('wb') as myfile:
            for chunk in stream.iter_content(chunk_size=1024):
                myfile.write(chunk)
        stream.close()

    def restore(self, snapshot):
        '''Restore Hashicorp Vault with the REST API'''
        pass

JOB = Vault
