'''Unit test for the cluster'''

from backup.cluster import Cluster

class TestCluster:
    def test_create(self):
        Cluster('MY_TEST', 'rsync', {
            'hosts': ['host01', 'host02', 'host03'],
            'paths': ['/var/log'],
            'run_style': 'seq',
            'slotdir': '/BACKUP/MY_TEST/slots',
        })
