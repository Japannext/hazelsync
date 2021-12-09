'''Basic tests on metrics'''

import time
import pytest
from datetime import datetime

from hazelsync.metrics import get_metrics_engine
from hazelsync.metrics import Dummy, Influxdb2, PrometheusPushGateway
from hazelsync.metrics import Gauge, Timer, Metric

def test_get_metrics_engine_dummy():
    config = {}
    engine = get_metrics_engine(config)
    assert isinstance(engine, Dummy)

def test_get_metrics_engine_prometheus():
    config = {'type': 'prometheus_pushgateway', 'address': 'localhost:9091'}
    engine = get_metrics_engine(config)
    assert isinstance(engine, PrometheusPushGateway)

def test_get_metrics_engine_influxdb2():
    config = {'type': 'influxdb2', 'address': 'http://localhost:8086', 'token': 'mysecret'}
    engine = get_metrics_engine(config)
    assert isinstance(engine, Influxdb2)

@pytest.fixture
def dummy():
    return Dummy({})

class TestGauge:
    def test_set(self, dummy):
        gauge = Gauge('mygauge', tags={'mytag1': None, 'mytag2': None}, engine=dummy)
        gauge.set(123, mytag1='a', mytag2='b')
        dummy.flush()

class TestTimer:
    def test_time(self, dummy):
        timer = Timer('mytimer', tags={'mytag1': None}, engine=dummy)
        with timer.time(mytag1='a'):
            time.sleep(0.01)
        assert isinstance(timer.start, datetime)
        assert isinstance(timer.stop, datetime)
        assert timer.start < timer.stop
