'''Test settings'''

import pytest
import yaml
from pytest_data.functions import get_data

from hazelsync.settings import GlobalSettings, ClusterSettings

class TestGlobalSettings:
    globals = {
        'default_backend': 'zfs',
        'job_options': {
            'rsync': {'user': 'root', 'private_key': '/etc/hazelsync.key'},
        },
        'backend_options': {
            'zfs': {'basedir': '/backup'},
        },
    }
    def test_init(self, global_path):
        g = GlobalSettings(global_path)
        assert g.default_backend == 'zfs'

    def test_job(self, global_path):
        g = GlobalSettings(global_path)
        assert g.job('rsync') == {'user': 'root', 'private_key': '/etc/hazelsync.key'}

    def test_backend(self, global_path):
        g = GlobalSettings(global_path)
        assert g.backend('zfs') == {'basedir': '/backup'}

class TestClusterSettings:
    globals = {
        'default_backend': 'zfs',
        'job_options': {
            'rsync': {'user': 'root', 'private_key': '/etc/hazelsync.key'},
        },
        'backend_options': {
            'zfs': {'basedir': '/backup'},
        },
    }
    clusters = {
        'mycluster1': {
            'job': 'rsync',
            'options': {
                'hosts': ['host01', 'host02', 'host03'],
                'paths': ['/opt/myapp'],
            },
        },
    }

    def test_init(self, global_path, clusterdir):
        ClusterSettings.directory = clusterdir
        c = ClusterSettings('mycluster1', global_path)
        assert c.job_type == 'rsync'

    def test_job(self, global_path, clusterdir):
        ClusterSettings.directory = clusterdir
        c = ClusterSettings('mycluster1', global_path)
        job_type, job_options = c.job()
        assert job_type == 'rsync'
        assert job_options['hosts'] == ['host01', 'host02', 'host03']
        assert job_options['paths'] == ['/opt/myapp']
        assert job_options['user'] == 'root'
        assert job_options['private_key'] == '/etc/hazelsync.key'

    def test_backend(self):
        pass
