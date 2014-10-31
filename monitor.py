from modules import Monitor
from modules import Heartbeat
import settings

listener = Monitor(settings.PORT, settings.SECRET_KEY, settings.NOTIFIERS)
listener.start()
print( "Monitor started" )
#heart = Heartbeat(settings.PORT, 2, settings.SECRET_KEY)
#heart.start()
#print("Started monitor heartbeat")
