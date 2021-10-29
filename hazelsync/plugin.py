'''Load and discover plugins'''

from enum import Enum
from importlib import import_module
from logging import getLogger
from typing import Optional

from pkg_resources import iter_entry_points

log = getLogger(__name__)

class PluginType(Enum):
    '''Type of plugin and their entrypoint name'''
    JOB = 'job'
    BACKEND = 'backend'
    SSH_HELPER = 'ssh_helper'

class Plugin:
    '''A plugin (job, backend, ssh_helper)'''
    def __init__(self, plugin_type: str):
        '''
        :param plugin_type: The type of plugin (ssh, backend or job).
        '''
        PluginType(plugin_type) # for validation
        self.type = plugin_type

    def get(self, name):
        '''
        Return the class associated with a plugin.
        Internal class should follow a naming convention that uses the plugin name
        and type capitalized.
        E.g. RsyncJob, ZfsBackend, RsynSsh, etc
        '''
        try:
            mod = import_module(f"hazelsync.{self.type}.{name}")
            class_name = name.capitalize() + self.type.capitalize()
            return getattr(mod, class_name)
        except ModuleNotFoundError:
            log.debug("Could not find plugin %s internally", name)
        matched_plugins = [ep for ep in iter_entry_points(f"hazelsync.{self.type}") if ep.name == name]
        if not matched_plugins:
            raise ModuleNotFoundError(f"Could not find {self.type} plugin '{name}'")
        log.debug("Found external plugin: %s", matched_plugins[0])
        return matched_plugins[0].load()
