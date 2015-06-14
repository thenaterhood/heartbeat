from heartbeat.monitoring import Monitor
from heartbeat.platform import Event, EventType
from heartbeat.network import NetworkInfo
from heartbeat.platform import get_config_manager
import subprocess


class SMARTMonitor(Monitor):

    def __init__(self, callback):
        settings = get_config_manager()
        self.check_drives = settings.monitoring.smartctl.drives
        self.threw_warning = False
        super(SMARTMonitor, self).__init__(callback)

    def run(self):
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
            event.type = EventType.WARNING
            self.callback(event)

        if (not foundProblem and self.threw_warning):
            net = NetworkInfo()
            self.threw_warning = False
            event = Event("SMART Message",
                          "A previous alert did not reoccur",
                          net.fqdn,
                          EventType.INFO
                          )
            self.callback(event)

    def _call_smartctl(self, drive):
        try:
            smartctl_out = subprocess.check_output(
                ['smartctl', '--health', drive])
            return ('PASSED' in str(smartctl_out))
        except:
            return False
