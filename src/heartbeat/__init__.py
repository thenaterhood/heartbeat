from heartbeat.modules import Heartbeat
from heartbeat.modules import HeartMonitor
from heartbeat.modules import HWMonitor
from heartbeat.modules import MonitorNode
import heartbeat.settings
import sys

def main():
    main_threads = dict()
    if (settings.HEARTBEAT):
        server = Heartbeat(settings.PORT, 2, settings.SECRET_KEY)
        server.daemon = True
        server.start()
        main_threads['heartbeat'] = server
        print("Heartbeat started. Hit ctrl+c to stop.")

    if (settings.MONITOR):
        monitor = HeartMonitor(settings.PORT, settings.SECRET_KEY, settings.NOTIFIERS)
        monitor.daemon = True
        monitor.cachefile = settings.HEARTBEAT_CACHE_DIR + "/heartbeats"
        monitor.start()
        print("Monitor started. Hit ctrl+c to stop.")
        main_threads['heartmonitor'] = monitor

    if (settings.ENABLE_HWMON):
        hwmon = HWMonitor(settings.HW_MONITORS, settings.NOTIFIERS)
        hwmon.daemon = True
        hwmon.start()
        print("Hardware monitoring started. Hit ctrl+c to stop.")
        main_threads['hwmon'] = hwmon

    if (settings.ENABLE_HISTAMINE):
        hwserver = MonitorNode('', settings.SECRET_KEY, settings.NOTIFIERS)
        hwserver.daemon = True
        hwserver.start()
        print("Hardware monitoring server started")
        main_threads['hwmonserv'] = hwserver

    for t in main_threads:
        main_threads[t].join()

