import os

_SERVER_ADDRESS = "yhpc3gkjqemsfpc4hcnfrvciil3xqgis4ipqfgootcgigawltlunxzqd.onion"
_SERVER_PORT = 5050
HIDDEN_SERVICE_PATH = f"{os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")}/hidden_service"
HIDDEN_SERVICE_ADDRESS = open(f"{HIDDEN_SERVICE_PATH}/hostname", "r").read().strip()[:-6]
HOST = "127.0.0.1"
PORT = 5025
SERVER_INFO = (_SERVER_ADDRESS, _SERVER_PORT)
