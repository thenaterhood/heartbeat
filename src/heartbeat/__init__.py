from heartbeat.modules import Heartbeat
from heartbeat.modules import HeartMonitor
from heartbeat.modules import MonitorHandler
from heartbeat.modules import HistamineNode
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

    if (settings.config['enable_monitor']):
        monitor = HeartMonitor(
            settings.config['port'], settings.config['secret_key'], notificationHandler)
        monitor.daemon = True
        monitor.cachefile = settings.config['cache_dir'] + "/heartbeats"
        monitor.start()
        print("Monitor started. Hit ctrl+c to stop.")
        main_threads['heartmonitor'] = monitor

    if (settings.config['enable_hwmonitor']):
        hwmon = MonitorHandler(settings.hwmonitors, notificationHandler)
        hwmon.daemon = True
        hwmon.start()
        print("Hardware monitoring started. Hit ctrl+c to stop.")
        main_threads['hwmon'] = hwmon

    if (settings.config['enable_histamine']):
        hwserver = HistamineNode(
            '', settings.config['secret_key'], notificationHandler)
        hwserver.daemon = True
        hwserver.start()
        print("Hardware monitoring server started")
        main_threads['hwmonserv'] = hwserver

    while threading.active_count() > 0:
        time.sleep(0.1)

