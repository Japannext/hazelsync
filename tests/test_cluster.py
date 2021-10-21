'''Unit test for the cluster'''

from hazelsync.cluster import Cluster

class TestCluster:
    def test_create(self, tmp_path):
        key = tmp_path / 'backup.key'
        key.write_text('')
        Cluster(
            name='MY_TEST',
            job_type='rsync',
            job_options={
                'hosts': ['host01', 'host02', 'host03'],
                'paths': ['/var/log'],
                'slotdir': '/BACKUP/MY_TEST/slots',
                'private_key': str(key),
            },
            backend_type="dummy",
        )
