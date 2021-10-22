'''A module for loading settings'''

from logging import getLogger
from pathlib import Path
from typing import Optional

import yaml

log = getLogger(__name__)

DEFAULT_SETTINGS = '/etc/hazelsync.yaml'
CLUSTER_DIRECTORY = '/etc/hazelsync.d'

class SettingError(AttributeError):
    '''Raise an exception if there is a configuration error'''
    def __init__(self, job, message):
        log.error("Configuration error (in %s): %s", job, message)
        super().__init__(message)

class Settings:
    '''A class to manage the settings'''
    def __init__(self,
        name: str,
        job_config: dict,
        global_config: Optional[dict] = None,
    ):
        self.name = name
        self.job_config = job_config
        log.debug("Job config: %s", self.job_config)
        self.global_config = global_config or {}
        log.debug("Global config: %s", self.global_config)

    @staticmethod
    def parse(name: str,
        global_settings: Path = DEFAULT_SETTINGS,
        clusterdir: Path = CLUSTER_DIRECTORY,
    ):
        '''Parse the settings
        :param name: The name of the job
        :param global_settings: Path to the global settings
        :param clusterdir: Path to the cluster drop-in directory
        '''
        global_settings = Path(global_settings)
        clusterdir = Path(clusterdir)
        if global_settings.is_file():
            log.debug("Reading %s", global_settings)
            glob = yaml.safe_load(global_settings.read_text(encoding='utf-8'))
        else:
            glob = {}
        jobfile = clusterdir / f"{name}.yaml"
        log.debug("Reading %s", jobfile)
        jobconfig = yaml.safe_load(jobfile.read_text(encoding='utf-8'))
        return Settings(name, jobconfig, glob)

    def job(self):
        '''Merge and return the type and configuration related to the job'''
        job_type = self.job_config.get('job')
        if not job_type:
            raise SettingError(self.name, 'Attribute "job" missing')
        defaults = self.global_config.get('job_options', {}).get(job_type, {})
        options = self.job_config.get('options', {})
        return job_type, {**defaults, **options}

    def backend(self):
        '''Merge and return the type and configuration related to the backend'''
        backend_type = self.job_config.get('backend') or self.global_config.get('default_backend')
        if not backend_type:
            raise SettingError(self.name, 'No backend defined. Define "backend" in the job configuration, or a "default_backend" in the global configuration')
        defaults = self.global_config.get('backend_options', {}).get(backend_type, {})
        options = self.job_config.get('backend_options', {})
        return backend_type, {**defaults, **options}
