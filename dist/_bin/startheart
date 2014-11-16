#!/usr/bin/env python

import heartbeat

if __name__ == "__main__":
    try:
        heartbeat.main()
    except (KeyboardInterrupt):
        print("Caught ctrl+c, shutting down Heartbeat...")
        if (settings.MONITOR):
            main_threads['heartmonitor'].saveCache()
        sys.exit(0)
