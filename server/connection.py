from socket import socket

from stem.control import Controller

from _config import HIDDEN_SERVICE_PATH, PORT, HOST


def send_response(client_socket: socket, response: str) -> None:
    """
    This function is responsible for sending a response to the client.
    """
    client_socket.sendall(response.encode() + b"\n\n")


def read_data(client_socket: socket.socket, return_bytes = False) -> str | bytes:
    """
    This function reads data from a socket until it finds the '\n\n' delimiter, indicating the end of a message. It returns the received data as a string or bytes, depending on the specified return_bytes flag.
    """
    data = b''
    while b'\n\n' not in data:
        data += client_socket.recv(1)

    return data.replace(b'\n\n', b'') if return_bytes else data.decode().strip()


def service_setup(host: str, post: int, socket: socket.socket) -> None:
    """
    This function sets up the hidden service
    """
    socket.bind((host, post))
    socket.listen(5)
    controller = Controller.from_port(address="127.0.0.1", port=9151)
    controller.authenticate()
    controller.set_options(
        [
            ("HiddenServiceDir", HIDDEN_SERVICE_PATH),
            ("HiddenServicePort", f"{PORT} {HOST}:{PORT}"),
            # If you want to add more hidden services, you can do so by adding more HiddenServiceDir and HiddenServicePort options.
            # Rememver to write all hidden services
            # ("HiddenServiceDir", "path/to/hidden_service_directory"),
            # ("HiddenServicePort", "port host:port"),

            # ("HiddenServiceDir", f"{_PROJECT_PATH}/src/hidden_services/server"),
            # ("HiddenServicePort", "5050 127.0.0.1:5050"),
        ]
    )
