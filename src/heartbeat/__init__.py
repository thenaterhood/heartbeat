from heartbeat.modules import Heartbeat
from heartbeat.modules import HeartMonitor
from heartbeat.modules import HWMonitor
from heartbeat.modules import HistamineNode
from heartbeat.settings import Configuration
import sys

def main():
    main_threads = dict()
    settings = Configuration()

    if (settings.config['enable_heartbeat']):
        server = Heartbeat(settings.config['port'], 2, settings.config['secret_key'])
        server.daemon = True
        server.start()
        main_threads['heartbeat'] = server
        print("Heartbeat started. Hit ctrl+c to stop.")

    if (settings.config['enable_monitor']):
        monitor = HeartMonitor(settings.config['port'], settings.config['secret_key'], settings.notifiers)
        monitor.daemon = True
        monitor.cachefile = settings.config['cache_dir'] + "/heartbeats"
        monitor.start()
        print("Monitor started. Hit ctrl+c to stop.")
        main_threads['heartmonitor'] = monitor

    if (settings.config['enable_hwmonitor']):
        hwmon = HWMonitor(settings.hwmonitors, settings.notifiers)
        hwmon.daemon = True
        hwmon.start()
        print("Hardware monitoring started. Hit ctrl+c to stop.")
        main_threads['hwmon'] = hwmon

    if (settings.config['enable_histamine']):
        hwserver = HistamineNode('', settings.config['secret_key'], settings.notifiers)
        hwserver.daemon = True
        hwserver.start()
        print("Hardware monitoring server started")
        main_threads['hwmonserv'] = hwserver

    for t in main_threads:
        main_threads[t].join()

