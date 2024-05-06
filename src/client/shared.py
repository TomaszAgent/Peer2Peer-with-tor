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
            ("HiddenServiceDir", "C:/Users/kuban/Projects/School/Peer2Peer-with-tor/src/client"),
            ("HiddenServicePort", "5000 127.0.0.1:5000"),
            # client_second
            ("HiddenServiceDir", "C:/Users/kuban/Projects/School/Peer2Peer-with-tor/src/client_second"),
            ("HiddenServicePort", "5025 127.0.0.1:5025"),
            # server
            ("HiddenServiceDir", "C:/Users/kuban/Projects/School/Peer2Peer-with-tor/src/server"),
            ("HiddenServicePort", "5050 127.0.0.1:5050"),
        ]
    )
