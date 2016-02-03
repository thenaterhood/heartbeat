"""
A collection of Heartbeat plugins for monitoring
disk status. Not all of these plugins will work on
every platform.

Configuration for each plugin is outline in its
specific class
"""

from heartbeat.monitoring import MonitorType
from heartbeat.plugin import Plugin
from heartbeat.platform import Event, Topics
from heartbeat.network import NetworkInfo
from heartbeat.platform import get_config_manager
import subprocess


class SMARTMonitor(Plugin):

    """
    Uses smartctl to query the SMART status of the hard drives.
    This plugin will work only on Unix systems with the smartctl
    utility installed.

    The disks to check can be configured by adding the following
    section to /etc/heartbeat/monitoring.conf (or the corresponding
    file on your install):

    smartctl:
        drives:
            - /dev/sda1
            - /dev/sda2
            ...
    """

    def __init__(self):
        settings = get_config_manager()
        self.check_drives = settings.monitoring.smartctl.drives
        self.threw_warning = False
        super(SMARTMonitor, self).__init__()

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
        Runs a SMART check on all the configured drives
        """

        foundProblem = False
        problemDrive = "Problem in "

        for d in self.check_drives:
            result = self._call_smartctl(d)
            if (not result):
                foundProblem = True
                problemDrive = problemDrive + d + ', '

        if (foundProblem):
            net = NetworkInfo()
            event = Event("SMART Alert", problemDrive, net.fqdn)
            event.type = Topics.WARNING
            callback(event)

        if (not foundProblem and self.threw_warning):
            net = NetworkInfo()
            self.threw_warning = False
            event = Event("SMART Message",
                          "A previous alert did not reoccur",
                          net.fqdn,
                          Topics.INFO
                          )
            callback(event)

    def _call_smartctl(self, drive):
        try:
            smartctl_out = subprocess.check_output(
                ['smartctl', '--health', drive])
            return ('PASSED' in str(smartctl_out))
        except Exception:
            return False
