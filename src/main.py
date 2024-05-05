import socket
import socks
from _thread import start_new_thread
from shared import read_data, service_setup
import json

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150, True)
HOST = "127.0.0.1"
PORT = 5000
CURRENT_MESSENGER = "other nick"
USER_NICK = "my nick"
SERVER_ADDRESS = "test"
SERVICE_DIR = "<SRC DIR>"


def messages_receiver(c: socket.socket):
    message = read_data(c)
    print(f'{CURRENT_MESSENGER}: {message}'.strip())


def messages_sender(c: socket.socket):
    # TODO: better look of user's messages
    while True:
        message = input()
        if message == "\\quit":
            break
        c.sendall(message.encode())


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    service_setup(HOST, PORT, s)
    with socks.socksocket() as ss:
        ss.connect((f"{SERVER_ADDRESS}.onion", 5050))
        register = input("Do you want to register? y/n")
        while register != "n":
            if register != "y":
                print("Select y or n")
                continue
            nick = input("nick (can't contain white spaces): ")
            if " " in nick:
                print("CAN'T CONTAIN WHITE SPACES")
                continue
            address = open(f"{SERVICE_DIR}/hostname", "r").read().strip()
            ss.sendall(f"NEW {nick} {address}".encode())
            res = read_data(ss)
            print(res)
            if res == "registered":
                break
            input("Do you want to register? y/n")
        ss.sendall("GET".encode())
        users = json.loads(read_data(ss))
        for user in users:
            print(user)
    # TODO: implement connecting to others
    # TODO: implement receiving messages in the background
    # TODO: implement saving nicks and addresses
    while True:
        c, _ = s.accept()
        start_new_thread(messages_receiver, (c,))
        start_new_thread(messages_sender, (c,))
