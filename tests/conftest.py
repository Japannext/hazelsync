'''Patches and fixtures for testing'''

import pytest
import yaml
from pytest_data.functions import get_data

GLOBALS = {
    'default_backend': 'zfs',
    'job_options': {
        'rsync': {'user': 'root', 'private_key': '/etc/hazelsync.key'},
    },
    'backend_options': {
        'zfs': {'basedir': '/backup'},
    },
}

@pytest.fixture
def global_path(tmp_path, request):
    path = tmp_path / 'hazelsync.yaml'
    data = get_data(request, 'globals', GLOBALS)
    text = yaml.dump(data)
    path.write_text(text)
    return path

def write_cluster(clusters, cluster_path):
    for cluster, config in clusters.items():
        text = yaml.dump(config)
        path = cluster_path / f"{cluster}.yaml"
        path.write_text(text)
    return cluster_path

@pytest.fixture
def clusterdir(tmp_path, request):
    cluster_path = tmp_path / 'hazelsync.d'
    cluster_path.mkdir()
    data = get_data(request, 'clusters', {})
    return write_cluster(data, cluster_path)

@pytest.fixture
def reportdir(tmp_path, request):
    report_path = tmp_path / 'reports'
    report_path.mkdir()
    data = get_data(request, 'reports', {})
    for cluster, reports in data.items():
        cluster_path = report_path / cluster
        cluster_path.mkdir()
        for timestamp, report in reports.items():
            text = yaml.dump(report)
            path = cluster_path / f"{timestamp}.yaml"
            path.write_text(text)
    return report_path

@pytest.fixture
def dummybackend(tmp_path, request):
    backend_path = tmp_path / 'backend'
    backend_path.mkdir()
    dummy = {
        'backend': 'dummy',
        'backend_options': {'tmp_dir': backend_path},
    }
    cluster_name = get_data(request, 'name', 'cluster01')
    data = get_data(request, 'cluster', {})
    data = {**dummy, **data}
    cluster_path = tmp_path / 'clusterdir'
    cluster_path.mkdir()
    write_cluster({cluster_name: data}, cluster_path)
