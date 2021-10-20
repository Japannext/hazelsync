'''A job to backup hashicorp Vault'''

import hvac

class Vault:
    def __init__(self,
        url: str,
        auth: dict,
    ):
        self.client = hvac.Client(
            url,
        )
        auth_method = auth.pop('method')
        try:
            getattr(self.client.auth, auth_method).login(**auth)
        except AttributeError as err:
            log.error(f"Auth method %s not supported by python hvac library", auth_method)
            raise err
        
    def backup(self, slot):
        stream = self.client.sys.take_raft_snapshot()
        stream.raise_for_status()
        with slot.open('wb') as f:
            for chunk in stream.iter_content(chunk_size=1024):
                f.write(chunk)
        stream.close()

    def restore(self, snapshot):
        pass
