'''Unit test for the cluster'''

from hazelsync.cluster import Cluster
from hazelsync.settings import Settings

class TestCluster:
    def test_create(self, tmp_path):
        key = tmp_path / 'backup.key'
        slots = tmp_path / 'slots'
        slots.mkdir()
        key.write_text('')
        cluster_settings = {
            'job': 'rsync',
            'options': {
                'hosts': ['host01', 'host02', 'host03'],
                'paths': ['/var/log'],
                'basedir': slots,
                'private_key': str(key),
            },
            'backend': 'dummy',
        }
        settings = Settings('MY_TEST', cluster_settings)
        Cluster(settings)
