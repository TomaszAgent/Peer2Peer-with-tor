from stem.control import Controller
import os


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
            # client
            ("HiddenServiceDir", os.getcwd().replace("\\", "/")),
            ("HiddenServicePort", f"5000 127.0.0.1:5000"),
            # server
            ("HiddenServiceDir", os.getcwd().replace("\\", "/")),
            ("HiddenServicePort", f"5050 127.0.0.1:5050"),
        ]
    )
