'''Load and discover plugins'''

from enum import Enum
from importlib import import_module
from logging import getLogger

from pkg_resources import iter_entry_points

log = getLogger('hazelsync')

class PluginType(Enum):
    '''Type of plugin and their entrypoint name'''
    JOB = 'job'
    BACKEND = 'backend'
    SSH_HELPER = 'ssh'

def get_plugin(plugin_type: str, name):
    '''
    Return the class associated with a plugin.
    Internal class should follow a naming convention that uses the plugin name
    and type capitalized.
    E.g. RsyncJob, ZfsBackend, RsynSsh, etc

    :param plugin_type: The type of plugin (ssh, backend or job).
    :param name: The name of the plugin
    '''
    try:
        PluginType(plugin_type) # for validation
    except ValueError as err:
        raise Exception(f"Invalid plugin type: {plugin_type}") from err
    try:
        mod = import_module(f"hazelsync.{plugin_type}.{name}")
        class_name = name.capitalize() + plugin_type.capitalize()
        return getattr(mod, class_name)
    except ModuleNotFoundError:
        log.debug("Could not find plugin %s internally", name)
    matched_plugins = [ep for ep in iter_entry_points(f"hazelsync.{plugin_type}") if ep.name == name]
    if not matched_plugins:
        raise ModuleNotFoundError(f"Could not find {plugin_type} plugin '{name}'")
    log.debug("Found external plugin: %s", matched_plugins[0])
    return matched_plugins[0].load()
