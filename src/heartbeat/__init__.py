from heartbeat.modules import Heartbeat
from heartbeat.modules import MonitorHandler
from heartbeat.modules import NotificationHandler
from heartbeat.platform import Configuration
import sys
import threading
import time
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(filename="/var/log/heartbeat.log")

def main(main_threads=None):
    logger.info("Starting heartbeat")
    if (main_threads == None):
        main_threads = dict()

    logger.debug("Loading configuration")
    settings = Configuration(load_modules=True)

    logger.debug("Bringing up notification/event handling")
    notificationHandler = NotificationHandler(settings.notifiers)

    if (settings.enable_heartbeat):
        logger.debug("Bringing up system heartbeat")
        server = Heartbeat(
            settings.port, 2, settings.secret_key)
        server.daemon = True
        server.start()
        main_threads['heartbeat'] = server
        print("Heartbeat started. Hit ctrl+c to stop.")

    if (settings.enable_hwmonitor):
        logger.debug("Bringing up monitoring subsystem")
        hwmon = MonitorHandler(settings.hwmonitors, notificationHandler)
        hwmon.daemon = True
        hwmon.start()
        print("Monitoring subsystem started. Hit ctrl+c to stop.")
        main_threads['hwmon'] = hwmon

    while threading.active_count() > 0:
        time.sleep(0.1)

    logger.info("Shutting down heartbeat")

