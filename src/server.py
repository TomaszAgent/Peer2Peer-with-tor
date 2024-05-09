import socket
from _thread import start_new_thread
from shared import read_data, service_setup
import json
import os
import time

USERS = {}
HOST = "127.0.0.1"
PORT = 5050


def connection_handler(c):
    while True:
        message = read_data(c)
        match message.split()[0]:
            case "NEW":
                if len(message.split()) > 4:
                    c.sendall("incorrect formatting\n".encode())
                    continue
                _, nick, address, port = message.split()
                if address in USERS.values():
                    c.sendall("address already registered\n".encode())
                    continue
                if nick in USERS:
                    c.sendall("nick unavailable\n".encode())
                    continue
                if not address.isalnum() or len(address) != 56:
                    c.sendall("incorrect address\n".encode())
                    continue
                USERS[nick] = (address, port)
                c.sendall("registered\n".encode())
            case "GET":
                c.sendall((json.dumps(USERS) + "\n").encode())
            case "CLOSE":
                nick = message.split()[1]
                USERS.pop(nick)
                c.close()
                return
            case _:
                c.sendall("unsupported request\n".encode())


def user_printer():
    while True:
        os.system('cls')
        print(f"There is {len(USERS)} user(s) connected: ")
        for user in USERS:
            print(f"{user}: {USERS[user]}")
        time.sleep(1)


start_new_thread(user_printer, ())
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    service_setup(HOST, PORT, s)
    while True:
        c, _ = s.accept()
        start_new_thread(connection_handler, (c,))
