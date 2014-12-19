from heartbeat.modules import Heartbeat
from heartbeat.modules import MonitorHandler
from heartbeat.modules import NotificationHandler
from heartbeat.platform import Configuration
import sys
import threading
import time


def main(main_threads=None):
    if (main_threads == None):
        main_threads = dict()

    settings = Configuration(load_modules=True)
    notificationHandler = NotificationHandler(settings.notifiers)

    if (settings.config['enable_heartbeat']):
        server = Heartbeat(
            settings.config['port'], 2, settings.config['secret_key'])
        server.daemon = True
        server.start()
        main_threads['heartbeat'] = server
        print("Heartbeat started. Hit ctrl+c to stop.")

    if (settings.config['enable_hwmonitor']):
        hwmon = MonitorHandler(settings.hwmonitors, notificationHandler)
        hwmon.daemon = True
        hwmon.start()
        print("Monitoring subsystem started. Hit ctrl+c to stop.")
        main_threads['hwmon'] = hwmon

    while threading.active_count() > 0:
        time.sleep(0.1)

