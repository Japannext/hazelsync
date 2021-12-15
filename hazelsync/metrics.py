'''Module about metrics management'''

from abc import abstractmethod
from dataclasses import dataclass, field as datafield
from typing import Optional, List
from datetime import datetime
from contextlib import contextmanager
from logging import getLogger

from influxdb_client import InfluxDBClient, Point
from prometheus_client import CollectorRegistry, Gauge as PromGauge, push_to_gateway

log = getLogger('hazelsync')

class MetricEngine:
    '''Abstract class for metric engine'''
    @abstractmethod
    def register(self, metrics):
        '''Register one or multiple metrics'''
    @abstractmethod
    def set(self, metric, value, tags):
        '''Create a point for a metric'''
    @abstractmethod
    def flush(self):
        '''Flush all metrics to the backend (if needed)'''

@dataclass
class Metric:
    '''Object to represent metrics'''
    name: str
    engine: MetricEngine
    field: str = ''
    additional_fields: dict = datafield(init=False, default_factory=dict)
    tags: dict = datafield(default_factory=dict)
    desc: Optional[str] = None

    def __post_init__(self):
        self.engine.register([self])
        self.fields = dict(self.additional_fields)

@dataclass
class Gauge(Metric):
    '''A gauge metric'''
    field: str = 'gauge'

    def set(self, value, **tags: dict):
        '''Set a gauge to a given value'''
        self.engine.set(self, value, {**self.tags, **tags})

@dataclass
class Timer(Gauge):
    '''A time metric'''
    start: datetime = datafield(init=False)
    stop: datetime = datafield(init=False)
    runtime: float = datafield(init=False)
    field: str = 'timer'

    def start_timer(self):
        '''Start the timer'''
        self.start = datetime.now()

    def stop_timer(self, **tags):
        '''Stop the timer and issue the metric'''
        self.stop = datetime.now()
        self.runtime = (self.stop - self.start).total_seconds()
        self.fields['start_time'] = self.start.timestamp()
        self.fields['stop_time'] = self.stop.timestamp()
        self.set(self.runtime, **tags)

    @contextmanager
    def time(self, **tags):
        '''A context manager for timing a call'''
        try:
            self.start_timer()
            yield
        finally:
            self.stop_timer(**tags)

class Dummy(MetricEngine):
    '''Metric engine doing nothing when nothing is configured'''
    def __init__(self, config):
        pass
    def register(self, metrics: List[Metric]):
        pass
    def set(self, metric, value, tags):
        pass
    def flush(self):
        pass

class PrometheusPushGateway(MetricEngine):
    '''Metric engine sending to a prometheus pushgateway'''
    def __init__(self, config):
        self.address = config.get('address')
        self.registry = CollectorRegistry()
        self.metrics = {}
    def register(self, metrics: List[Metric]):
        '''Create prometheus metrics'''
        for metric in metrics:
            name = f"{metric.name}_{metric.field}"
            log.debug("Registrating metric %s to prometheus engine", name)
            self.metrics[name] = PromGauge(metric.name,
                metric.desc, metric.tags.keys(), registry=self.registry)
        log.debug("Prom metrics: %s", self.metrics)
    def set(self, metric, value, tags):
        '''Set a gauge metric'''
        log.debug("Attempting to set %s@%s: %s (%s)", metric.name, metric.field, value, tags)
        prom_metric = self.metrics.get(f"{metric.name}_{metric.field}")
        log.debug("Found prom_metric: %s", prom_metric)
        prom_metric.labels(**tags).set(value)
    def flush(self):
        '''Push all collected metrics to Prometheus pushgateway'''
        push_to_gateway(self.address, job='hazelsync', registry=self.registry)

class Influxdb2(MetricEngine):
    '''Metric engine sending to InfluxDB v2 API'''
    def __init__(self, config):
        address = config.get('address')
        token = config.get('token')
        write_options = config.get('write_options', {})
        self.api = InfluxDBClient(url=address, token=token).write_api(**write_options)
        self.bucket = config.get('bucket', 'hazelsync')
    def register(self, metrics: List[Metric]):
        '''Registrating a metric'''
    def set(self, metric, value, tags):
        '''Sending a metric through the write API'''
        fields = {metric.field: value, **metric.fields}
        log.debug('Attempting to set %s@%s: %s (%s | %s)', metric.name, metric.field, value, tags, fields)
        record = dict(measurement=metric.name, tags=tags, fields=fields)
        point = Point.from_dict(record)
        log.debug('Point: %s', point)
        self.api.write(bucket=self.bucket, record=[point])
    def flush(self):
        '''Terminating all batches'''
        log.debug('Flushing the API write batch')
        self.api.close()

def get_metrics_engine(config: dict) -> MetricEngine:
    '''Detect the metric engine used by the config
    and return it'''
    mytype = config.get('type', None)
    if mytype == 'prometheus_pushgateway':
        return PrometheusPushGateway(config)
    if mytype == 'influxdb2':
        return Influxdb2(config)
    return Dummy(config)
