'''Unit test for the cluster'''

from hazelsync.cluster import Cluster
from hazelsync.settings import ClusterSettings

class TestCluster:
    clusters = {
        'mycluster01': {
            'job': 'rsync',
            'options': {
                'hosts': ['host01', 'host02', 'host03'],
                'paths': ['/var/log'],
            },
            'backend': 'dummy',
        },
    }

    def test_create(self, global_path, clusterdir):
        ClusterSettings.directory = clusterdir
        settings = ClusterSettings('mycluster01', global_path)
        Cluster(settings)
