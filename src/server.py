import socket
from _thread import start_new_thread
from shared import read_data, service_setup
import json

USERS = {}
HOST = "127.0.0.1"
PORT = 5050


def connection_handler(c):
    while True:
        message = read_data(c)
        match message.split()[0]:
            case "NEW":
                if len(message.split()) > 3:
                    c.sendall("incorrect formatting".encode())
                    continue
                _, nick, address = message.split()
                if nick in USERS:
                    c.sendall("nick unavailable".encode())
                    continue
                if address in USERS.values():
                    c.sendall("address already registered".encode())
                    continue
                if not address.isalnum() or len(address) != 56:
                    c.sendall("incorrect address")
                    continue
                USERS[nick] = address
            case "GET":
                c.sendall((json.dumps(USERS) + "\n").encode())
            case "CLOSE":
                c.close()
                return
            case _:
                c.sendall("unsupported request")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    service_setup(HOST, PORT, s)
    while True:
        c, _ = s.accept()
        start_new_thread(connection_handler, (c,))
