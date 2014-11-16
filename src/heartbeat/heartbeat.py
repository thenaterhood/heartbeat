from modules import Heartbeat
from modules import HeartMonitor
from modules import HWMonitor
import settings
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

    for t in main_threads:
        main_threads[t].join()

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt):
        print("Caught ctrl+c, shutting down Heartbeat...")
        if (settings.MONITOR):
            main_threads['heartmonitor'].saveCache()
        sys.exit(0)


