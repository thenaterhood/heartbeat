from modules import Heartbeat
from modules import HeartMonitor
from modules import HWMonitor
import settings
import sys

if __name__ == "__main__":
    try:
        main_threads = []
        if (settings.HEARTBEAT):
            server = Heartbeat(settings.PORT, 2, settings.SECRET_KEY)
            server.daemon = True
            server.start()
            main_threads.append(server)
            print("Heartbeat started. Hit ctrl+c to stop.")

        if (settings.MONITOR):
            monitor = HeartMonitor(settings.PORT, settings.SECRET_KEY, settings.NOTIFIERS)
            monitor.daemon = True
            monitor.start()
            print("Monitor started. Hit ctrl+c to stop.")
            main_threads.append(monitor)

        if (settings.ENABLE_HWMON):
            hwmon = HWMonitor(settings.HW_MONITORS, settings.NOTIFIERS)
            hwmon.daemon = True
            hwmon.start()
            print("Hardware monitoring started. Hit ctrl+c to stop.")
            main_threads.append(hwmon)

        for t in main_threads:
            t.join()

    except (KeyboardInterrupt):
        print("Caught ctrl+c, shutting down Heartbeat...")
        sys.exit(0)
