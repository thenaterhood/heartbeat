import socket
import sys
import json
from heartbeat.platform import Event
from heartbeat.network import NetworkInfo

def print_help():
    helptext="""
    Send an event to heartbeat.

    Usage:
    heartbeat-send event [payload]

    event and payload are JSON strings.

    Examples:
    heartbeat-send '{"title": "Example", "message": "Hello, world", "type": "INFO"}'
    heartbeat-send '{"title": "Test", "message": "Error", "type": "ERROR"}' '{"errno": "123"}'
    """

    print(helptext)

def main():
    if len(sys.argv) == 1:
        print_help()
        sys.exit(1)

    event_json = sys.argv[1]
    try:
        event = Event.from_json(event_json) # sanitization step
    except Exception as e:
        print(str(e), file=sys.stderr)
        print_help()
        sys.exit(1)
    event.source = 'LocalSocket'
    event.host = NetworkInfo().get_fqdn()
    if len(sys.argv) > 2:
        try:
            event.payload = json.loads(sys.argv[2])
        except Exception as e:
            print("Malformed payload JSON", file=sys.stderr)
            print_help()
            sys.exit(1)
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        client.connect('/tmp/heartbeat.sock')
    except FileNotFoundError:
        print("Unable to connect to heartbeat socket", file=sys.stderr)
        sys.exit(1)

    client.send(bytes(event.to_json().encode("UTF-8")))

if __name__ == '__main__':
    main()
