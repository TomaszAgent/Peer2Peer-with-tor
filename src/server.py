import socket
from _thread import start_new_thread
from shared import read_data, service_setup
import json

USERS = {}
HOST = "127.0.0.1"
PORT = 5050


def connection_handler(c):
    message = read_data(c)
    match message.split()[0]:
        case "NEW":
            if len(message.split()) > 3:
                c.sendall("incorrect formatting".encode())
                c.close()
                return
            _, nick, address = message.split()
            if nick in USERS:
                c.sendall("nick unavailable".encode())
                c.close()
                return
            if address in USERS.values():
                c.sendall("address already registered".encode())
                c.close()
                return
            if not address.isalnum() or len(address) != 56:
                c.sendall("incorrect address")
                c.close()
                return
            USERS[nick] = address
        case "GET":
            c.sendall(json.dumps(USERS).encode())
            c.close()
        case _:
            c.sendall("unsupported request")
            c.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    service_setup(HOST, PORT, s)
    while True:
        c, _ = s.accept()
        start_new_thread(connection_handler, (c,))
