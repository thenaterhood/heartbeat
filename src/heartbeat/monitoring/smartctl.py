from heartbeat.monitoring import Monitor
from heartbeat.platform import Event
from heartbeat.network import NetworkInfo
from heartbeat.platform import Configuration
import subprocess


class SMARTMonitor(Monitor):

    def __init__(self, callback):
        settings = Configuration()
        self.check_drives = settings.config['heartbeat.hwmonitors.smartctl']['drives']
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
            self.callback(event)

    def _call_smartctl(self, drive):
        try:
            smartctl_out = subprocess.check_output(
                ['smartctl', '--health', drive])
            return ('PASSED' in str(smartctl_out))
        except:
            return False
