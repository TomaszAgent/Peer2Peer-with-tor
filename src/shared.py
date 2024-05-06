import os
import socket
from stem.control import Controller

PROJECT_PATH = os.getcwd().replace("\\", "/")


def read_data(client_socket: socket.socket) -> str:
    """
    Reads data from a socket
    """
    data = b''
    while b'\n' not in data:
        data += client_socket.recv(1)

    return data.decode().strip()


def service_setup(host: str, post: int, socket: socket.socket) -> None:
    """
    Set up a hidden service for the server and clients
    """
    socket.bind((host, post))
    socket.listen(5)
    controller = Controller.from_port(address="127.0.0.1", port=9151)
    controller.authenticate()
    controller.set_options(
        [
            # Client 1
            ("HiddenServiceDir", f"{PROJECT_PATH}/src/hidden_services/clients/client1"),
            ("HiddenServicePort", "5000 127.0.0.1:5000"),
            # Client 2
            ("HiddenServiceDir", f"{PROJECT_PATH}/src/hidden_services/clients/client2"),
            ("HiddenServicePort", "5025 127.0.0.1:5025"),
            # Server
            ("HiddenServiceDir", f"{PROJECT_PATH}/src/hidden_services/server"),
            ("HiddenServicePort", "5050 127.0.0.1:5050"),
        ]
    )
