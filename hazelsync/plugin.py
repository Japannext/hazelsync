'''Load and discover plugins'''

from enum import Enum
from pkg_resources import iter_entry_points
from importlib import import_module
import pkg_resources
from logging import getLogger

log = getLogger(__name__)

class PluginType(Enum):
    '''Type of plugin and their entrypoint name'''
    JOB = 'job'
    BACKEND = 'backend'

class Plugin:
    def __init__(self, plugin_type: str):
        PluginType(plugin_type) # for validation
        self.type = plugin_type

    def get(self, name):
        '''Return the class associated with a plugin'''
        try:
            mod = import_module(f"hazelsync.{self.type}.{name}")
            return getattr(mod, name.capitalize())
        except ModuleNotFoundError:
            log.debug("Could not find plugin %s internally", name)
        matched_plugins = [ep for ep in iter_entry_points(f"hazelsync.{self.type}") if ep.name == name]
        if not matched_plugins:
            raise ModuleNotFoundError(f"Could not find {self.type} plugin '{name}'")
        log.debug("Found external plugin: %s", matched_plugins[0])
        return matched_plugins[0].load()
