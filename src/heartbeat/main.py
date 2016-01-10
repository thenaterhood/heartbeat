#!/bin/env python3
import sys, os

if (sys.version_info < (3, 3)):
    sys.path.append('/lib/python3.2/site-packages')

from heartbeat.modules import Heartbeat
from heartbeat.modules import MonitorHandler
from heartbeat.modules import EventServer
from heartbeat.network import SocketBroadcaster
from heartbeat.platform import get_config_manager, load_notifiers, load_monitors
from heartbeat.monitoring import MonitorType
from heartbeat.plugin import PluginRegistry, ModuleLoader
import threading
import time
import logging, logging.handlers
import concurrent.futures

# Temporary include until full API upgrade TODO
# @deprecated
import inspect


logger = logging.getLogger("heartbeat")
logger.setLevel(logging.DEBUG)
try:
    filehandler = logging.handlers.TimedRotatingFileHandler(
            filename='/var/log/heartbeat.log',
            when='W0'
            )
except Exception:
    print("No write permissions to log directory. Using current directory")
    filehandler = logging.handlers.TimedRotatingFileHandler(
            filename="./heartbeat.log",
            when="W0"
            )
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(name)s;%(message)s",
                              "%Y-%m-%d %H:%M:%S")
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)
termhandler = logging.StreamHandler(sys.stdout)
termhandler.setLevel(logging.INFO)
logger.addHandler(termhandler)

def main():
    threads = []
    active_plugins = []

    logger.debug("Loading configuration")
    settings = get_config_manager()

    logger.debug("Loading plugins")

    if settings.heartbeat.plugins is not None and len(settings.heartbeat.plugins) > 0:
        PluginRegistry.populate_whitelist(settings.heartbeat.plugins)
        for p in settings.heartbeat.plugins:
            ModuleLoader.load(p, full_classpath=True)

    load_notifiers(settings.heartbeat.notifiers)
    load_monitors(settings.heartbeat.monitors)

    for name, plugin in PluginRegistry.plugins.items():
        # TODO

        # @deprecated
        if len(inspect.getargspec(plugin.__init__).args) > 1:
            active_plugins.append(plugin(None))
        else:
            active_plugins.append(plugin())

    logger.info("Bringing up notification/event handling")
    notifyPool = concurrent.futures.ThreadPoolExecutor(max_workers=5)
    notifiers = load_notifiers(settings.heartbeat.notifiers)

    dispatcher = EventServer(notifyPool)

    for plugin in active_plugins:
        for t, c in plugin.get_subscriptions().items():
            dispatcher.attach(t, c)

    if (settings.heartbeat.enable_heartbeat):
        logger.info("Bringing up system heartbeat")
        broadcaster = SocketBroadcaster(
                settings.heartbeat.port,
                settings.heartbeat.monitor_server
                )
        server = Heartbeat(
            2,
            settings.heartbeat.secret_key,
            broadcaster,
            logger
            )
        server.start()
        threads.append(server)

    if (settings.heartbeat.enable_hwmonitor):
        logger.info("Bringing up monitoring")
        required_workers = 1
        monitorPool = concurrent.futures.ThreadPoolExecutor(
                max_workers=len(settings.heartbeat.monitors)
                    )
        hwmon = MonitorHandler(
                dispatcher.put_event,
                monitorPool,
                logger
                )

        for plugin in active_plugins:

            producers = plugin.get_producers()
            for t, c in producers.items():
                required_workers += 1
                if t == MonitorType.REALTIME:
                    hwmon.add_realtime_monitor(c)
                elif t == MonitorType.PERIODIC:
                    hwmon.add_periodic_monitor(c)

        hwmon.threadpool = concurrent.futures.ThreadPoolExecutor(
                max_workers = required_workers
                )

        hwmon.start()
        threads.append(hwmon)

    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        for t in threads:
            t.shutdown = True

        print("Shutting down heartbeat...")
        time.sleep(5)
        os._exit(1)


if __name__ == "__main__":

    main()
