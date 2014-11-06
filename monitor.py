from modules import Monitor
from modules import Heartbeat
import settings
import sys

if __name__ == "__main__":
    try:
        listener = Monitor(settings.PORT, settings.SECRET_KEY, settings.NOTIFIERS)
        listener.daemon = True
        listener.start()
        print("Monitor started. Use ctrl+c to stop.")
        listener.join()
    except KeyboardInterrupt:
        print("ctrl+c received, shutting down monitor")
        sys.exit(0)
#heart = Heartbeat(settings.PORT, 2, settings.SECRET_KEY)
#heart.start()
#print("Started monitor heartbeat")
