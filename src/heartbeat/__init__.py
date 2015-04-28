from heartbeat.modules import Heartbeat
from heartbeat.modules import MonitorHandler
from heartbeat.modules import NotificationHandler
from heartbeat.network import SocketBroadcaster
from heartbeat.platform import get_config_manager, load_notifiers, load_monitors
import sys, os
import threading
import time
import logging, logging.handlers


logger = logging.getLogger(__name__)
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

def main(main_threads=None):
    logger.info("Starting heartbeat")
    if (main_threads == None):
        main_threads = dict()

    logger.debug("Loading configuration")
    settings = get_config_manager()

    logger.info("Bringing up notification/event handling")
    notifiers = load_notifiers(settings.heartbeat.notifiers)
    notificationHandler = NotificationHandler(notifiers)

    if (settings.heartbeat.enable_heartbeat):
        logger.info("Bringing up system heartbeat")
        broadcaster = SocketBroadcaster(
                settings.heartbeat.port,
                settings.heartbeat.monitor_server
                )
        server = Heartbeat(
            2,
            settings.heartbeat.secret_key,
            broadcaster
            )
        server.daemon = True
        server.start()
        main_threads['heartbeat'] = server

    if (settings.heartbeat.enable_hwmonitor):
        logger.info("Bringing up monitoring subsystem")
        monitors = load_monitors(settings.heartbeat.monitors)
        hwmon = MonitorHandler(monitors, notificationHandler)
        hwmon.daemon = True
        hwmon.start()
        main_threads['hwmon'] = hwmon

    for t in main_threads.values():
        t.join()

    logger.info("Shutting down heartbeat")

if __name__ == "__main__":
    main()
