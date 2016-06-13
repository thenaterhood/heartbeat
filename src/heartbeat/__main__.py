#!/bin/env python3
import sys, os

if (sys.version_info < (3, 3)):
    sys.path.append('/lib/python3.2/site-packages')

from heartbeat.routing import EventRouter
from heartbeat.platform import get_config_manager
from heartbeat.monitoring import MonitorType, MonitorHandler
from heartbeat.plugin import PluginRegistry
import time
import logging, logging.handlers
import concurrent.futures
import signal

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

class SignalHandling(object):
    """
    Does graceful signal handling for heartbeat.
    """
    def __enter__(self):
        signal.signal(signal.SIGQUIT, exit_heartbeat)
        signal.signal(signal.SIGTERM, exit_heartbeat)
        signal.signal(signal.SIGINT, exit_heartbeat)

    def __exit__(self, type, value, traceback):
        # Ideally this would restore the original
        # signal handlers, but that isn't functionality
        # that's needed right now, so we'll do nothing.
        pass


def exit_heartbeat(signal, frame):
    logger.debug("Received signal %i. Exiting gracefully.", signal)
    for p in PluginRegistry.get_active_plugins():
        logger.debug("Calling halt() on %s", str(p))
        p.halt()

    logger.info("Waiting 5 seconds for plugins to halt, then exiting...")
    time.sleep(5)

    os._exit(0)

def main():
    if (sys.version_info < (3, 3)):
        logger.error("Your Python version is older than 3.3. It is no longer officially supported!")

    threads = []

    logger.debug("Loading configuration")
    settings = get_config_manager()

    logger.debug("Loading plugins")
    PluginRegistry.populate_from_settings(settings)
    PluginRegistry.activate_plugins()

    logger.info("Bringing up notification/event handling")
    notifyPool = concurrent.futures.ThreadPoolExecutor(max_workers=5)

    dispatcher = EventRouter(notifyPool)

    hwmon = MonitorHandler(
        event_callback=dispatcher.put_event,
        interval=settings.heartbeat.query_interval,
        threadpool=None,
        logger=logger
    )

    required_workers = 1

    for plugin in PluginRegistry.get_active_plugins():
        for t, c in plugin.get_subscriptions().items():
            dispatcher.attach(t, c)
        for t, c in plugin.get_producers().items():
            required_workers += 1
            if t == MonitorType.REALTIME:
                hwmon.add_realtime_monitor(c)
            elif t == MonitorType.PERIODIC:
                hwmon.add_periodic_monitor(c)

    hwmon.threadpool = concurrent.futures.ThreadPoolExecutor(
            max_workers = required_workers
            )

    with SignalHandling() as sh:
        hwmon.start()
        while 1:
            time.sleep(1)

if __name__ == "__main__":
    main()
