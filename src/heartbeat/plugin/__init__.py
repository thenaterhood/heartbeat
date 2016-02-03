import importlib
import logging
import traceback
from random import shuffle
from heartbeat.platform import get_config_manager


class ModuleLoader(object):

    """
    Dynamically loads modules at runtime for loading plugins.
    """

    def load_multiple(paths, full_classpath=False):
        """
        Loads multiple modules from a module path or a full classpath

        Params:
            Array paths: A list of paths to load
            Bool full_classpath: Whether the paths provided are a full classpath
        """
        modules = []
        for p in paths:
            modules.append(ModuleLoader.load_module(p, full_classpath))

        return modules

    def load(path, full_classpath=False):
        """
        Loads a single module from a path

        Params:
            String path: the path to load
            Bool full_classpath: Whether the path provided is a full classpath
        """
        if full_classpath:
            path = ".".join(path.split(".")[:-1])

        module = importlib.import_module(path)
        return module


class PluginRegistry(type):

    """
    Registry of loaded plugins. This is populated automatically
    when plugins are imported.

    This relies on a whitelist, populated from the configuration and
    will attempt to only import plugins that are configured.
    """

    plugins = []
    active_plugins = []
    whitelist = []
    available_services = []
    logger = logging.getLogger(
        __name__ + ".PluginRegistry"
        )

    def __init__(cls, name, bases, attrs):
        full_class = cls.__module__ + "." + name
        if name != 'Plugin' and full_class in PluginRegistry.whitelist:
            PluginRegistry.logger.debug(
                "Discovered plugin %s.%s;",
                cls.__module__,
                name
            )
            PluginRegistry.plugins.append(cls)

    def activate_plugins():
        """
        Instantiates all the plugins in the plugin registry
        """
        waiting_plugins = PluginRegistry.plugins
        i = 0
        tries = 0

        while len(waiting_plugins) > 0 and tries < 10:
            if i >= len(waiting_plugins):
                i = 0
                tries += 1
                shuffle(waiting_plugins)

            try:
                plugin = waiting_plugins[i]()
                if plugin.requirements_satisfied(PluginRegistry.available_services):
                    PluginRegistry.active_plugins.append(plugin)
                    PluginRegistry.logger.debug(
                            "Activated plugin %s",
                            str(waiting_plugins[i])
                            )
                    PluginRegistry.available_services += plugin.get_services()
                    del(waiting_plugins[i])
                else:
                    i += 1
            except Exception as err:
                summary = traceback.extract_tb(err.__traceback__)[-1]
                PluginRegistry.logger.error(
                        "Failed to activate %s: %s at %s:%d",
                        str(waiting_plugins[i]),
                        str(err),
                        summary.filename,
                        summary.lineno
                        )
                i += 1

        for i in waiting_plugins:
            PluginRegistry.logger.error(
                    "Failed to activate %s, %s",
                    str(i),
                    "Requirements could not be satisfied"
                    )

    def populate_whitelist(allowed_plugins):
        """
        Populates the plugin whitelist with a list of allowed plugins

        Parameters:
            Array[str] allowed_plugins
        """
        if PluginRegistry.whitelist == []:
            PluginRegistry.whitelist = allowed_plugins
        else:
            raise Exception("The PluginRegistry whitelist has already been configured")

    def populate_from_settings(settings=None):
        """
        Populates the plugin registry from the settings

        Paremeters:
            ConfigManager settings: defaults to None
        """
        if settings is None:
            settings = get_config_manager()

        if settings.heartbeat.plugins is None:
            return None

        PluginRegistry.populate_whitelist(settings.heartbeat.plugins)

        for p in settings.heartbeat.plugins:
            try:
                ModuleLoader.load(p, full_classpath=True)
            except ImportError:
                PluginRegistry.logger.warning("Failed to import plugin %s", p)


class Plugin(object, metaclass=PluginRegistry):

    """
    The base heartbeat Plugin class that all plugins are
    required to inherit from. When inheriting classes are
    imported, they will automatically be registered with
    the PluginRegistry if they appear in the configuration.
    """

    def get_subscriptions(self):
        """
        Returns a dictionary of topics mapped to
        callbacks which heartbeat will set up.
        The default at this level is an empty
        dictionary.

        Returns:
            dict(Topic: Callback)
        """
        return {}

    def get_producers(self):
        """
        Returns a dictionary of producers and types
        (realtime and otherwise) that will produce
        Events that heartbeat will dispatch. The default
        at this level is an empty dictionary.

        Returns:
            dict(MonitorType: Callback)
        """
        return {}

    def get_services(self):
        """
        Returns a list of services provided by the plugin.
        This is a list of strings that match with the
        service requirements of other plugins.

        Multiple plugins can provide the same service.
        Service names are arbitrary and only observed for
        matching plugin dependencies with the providers.

        Returns:
            String[] services
        """
        return []

    def requirements_satisfied(self, avail_services=None):
        """
        Returns whether the plugin's requirements are
        satisfied. This method is implemented fully here,
        but Plugin subclasses may wish to override it
        for their specific needs (such as considering
        their requirements fulfilled by multiple services
        or optional requirements).

        Params:
            String[] avail_services: services available

        Returns:
            bool
        """
        if set(self.get_required_services()).issubset(avail_services):
            return True

        return False

    def get_required_services(self):
        """
        Returns a list of required services. Service names
        should be unique, either by using a unique name or
        something like a uuid. When heartbeat loads plugins,
        it expects the service requirements to be fulfilled
        by another Plugin. Multiple Plugins can provide the
        same service, but they need to provide compatible
        payloads (additional data for another service is fine,
        but missing data is not).

        Dependencies must be explicitly enabled by the
        user or they will not be made available.

        Plugins should not interact with each other directly,
        but certain plugins may listen for events produced by
        specific other plugins, such as a heartbeat monitor
        requiring a plugin that will listen to network
        heartbeats.

        Returns:
            String[] services
        """
        return []
