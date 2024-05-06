from stem.control import Controller
import os

PROJECT_PATH = os.getcwd().replace("\\", "/")


def read_data(c):
    data = b''
    while b'\n' not in data:
        data += c.recv(1)

    return data.decode().strip()


def service_setup(h, p, s):
    s.bind((h, p))
    s.listen(5)
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
