#!/bin/env python3
import sys, os

if (sys.version_info < (3, 3)):
    sys.path.append('/lib/python3.2/site-packages')

from heartbeat.modules import EventServer
from heartbeat.platform import get_config_manager
from heartbeat.monitoring import MonitorType, MonitorHandler
from heartbeat.plugin import PluginRegistry
import time
import logging, logging.handlers
import concurrent.futures

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
    if (sys.version_info < (3, 3)):
        logger.info("Support for Python 3.2 will be dropped soon!")

    threads = []

    logger.debug("Loading configuration")
    settings = get_config_manager()

    logger.debug("Loading plugins")
    PluginRegistry.populate_from_settings(settings)
    PluginRegistry.activate_plugins()

    logger.info("Bringing up notification/event handling")
    notifyPool = concurrent.futures.ThreadPoolExecutor(max_workers=5)

    dispatcher = EventServer(notifyPool)
    hwmon = MonitorHandler(
        dispatcher.put_event,
        None,
        logger
    )

    required_workers = 1

    for plugin in PluginRegistry.active_plugins:
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
