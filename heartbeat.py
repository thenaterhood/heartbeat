from modules import Heartbeat
import settings
import sys

if __name__ == "__main__":
    try:
        server = Heartbeat(settings.PORT, 2, settings.SECRET_KEY)
        server.daemon = True
        server.start()
        print("Heartbeat started. Hit ctrl+c to stop.")
        server.join()
    except (KeyboardInterrupt):
        print("Caught ctrl+c, shutting down Heartbeat...")
        sys.exit(0)
