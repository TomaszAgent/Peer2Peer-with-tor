import os

_SERVER_ADDRESS = ""
_SERVER_PORT = 5001
HOST = "127.0.0.1"
PORT = 5050

# Don't change this
SERVER_INFO = (_SERVER_ADDRESS, _SERVER_PORT)
HIDDEN_SERVICE_PATH = f"{os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")}/hidden_service"
HIDDEN_SERVICE_ADDRESS = open(f"{HIDDEN_SERVICE_PATH}/hostname", "r").read().strip()[:-6]
