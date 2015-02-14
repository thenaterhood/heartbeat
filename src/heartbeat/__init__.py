from heartbeat.modules import Heartbeat
from heartbeat.modules import MonitorHandler
from heartbeat.modules import NotificationHandler
from heartbeat.platform import Configuration
import sys
import threading
import time
import logging, logging.handlers


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
filehandler = logging.handlers.TimedRotatingFileHandler(filename='/var/log/heartbeat.log', when='W0')
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
    settings = Configuration(load_modules=True)

    logger.info("Bringing up notification/event handling")
    notificationHandler = NotificationHandler(settings.notifiers)

    if (settings.enable_heartbeat):
        logger.info("Bringing up system heartbeat")
        server = Heartbeat(
            settings.port, 2, settings.secret_key)
        server.daemon = True
        server.start()
        main_threads['heartbeat'] = server

    if (settings.enable_hwmonitor):
        logger.info("Bringing up monitoring subsystem")
        hwmon = MonitorHandler(settings.hwmonitors, notificationHandler)
        hwmon.daemon = True
        hwmon.start()
        main_threads['hwmon'] = hwmon

    while threading.active_count() > 0:
        time.sleep(0.1)

    logger.info("Shutting down heartbeat")

