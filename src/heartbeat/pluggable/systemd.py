from heartbeat.plugin import Plugin
from heartbeat.platform import Event, get_config_manager
from heartbeat.monitoring import MonitorType
from heartbeat.network import NetworkInfo
import subprocess

class Service(Plugin):

    """
    Checks a systemd service to check if it has failed.
    This is NOT written as a realtime monitor.

    The services to monitor can be configured by adding the following
    section to /etc/heartbeat/monitoring.conf (or your install's
    corresponding location):

    systemd:
        services:
            - service1
            - service2
    """

    def __init__(self, settings=None):
        if settings is None:
            settings = get_config_manager()

        self.monitored_services = settings.monitoring.systemd.services
        self.fqdn = NetworkInfo().get_fqdn()

    def get_producers(self):
        """
        Overrides Plugin.get_producers
        """
        prods = {
            MonitorType.PERIODIC: self.run_check
        }

        return prods

    def run_check(self, callback):
        """
        Runs a check on all the services the plugin is configured
        to be paying attention to
        """
        for s in self.monitored_services:
            running = self._process_running(s)
            if not running:
                callback(
                    Event(
                        "Service Failed",
                        s + " failed",
                        self.fqdn
                    )
                )

    def _process_running(self, service):
        """
        Checks a single service by calling systemd and checking
        the outputself.
        """
        try:
            out = subprocess.check_output(
                ['systemctl', 'status', service]
            )
            return (
                "Active: active (running)" in str(out) or
                "Active: active (listening)" in str(out))
        except Exception:
            return False
