from modules import Heartbeat
import settings

server = Heartbeat(settings.PORT, 2, settings.SECRET_KEY)
server.start()
print("Heartbeat started")
