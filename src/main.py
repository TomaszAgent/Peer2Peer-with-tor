import socket
import socks
from _thread import start_new_thread
from shared import read_data, service_setup
import json
import os
import time


socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150, True)
HOST = "127.0.0.1"
PORT = 5000
CURRENT_MESSENGER = "other nick"
USER_NICK = "my nick"
SERVER_ADDRESS = "kjopruomiwhvm7zzouhivnft4uuhiym5jhifrrtw3mqlaps666jfioad"
SERVICE_DIR = os.getcwd().replace("\\", "/")
MESSAGES = {}
MESSAGING = False


def messages_receiver(c: socket.socket, messenger):
    if messenger not in MESSAGES:
        MESSAGES[messenger] = []
    while True:
        message = read_data(c)
        MESSAGES[messenger].append(f"{messenger}: {message}")


def messages_sender(c: socket.socket):
    global MESSAGING
    MESSAGING = True
    while True:
        message = input()
        if message == "\\quit":
            MESSAGING = False
            break
        c.sendall(message.encode())
        MESSAGES[CURRENT_MESSENGER].append(f'You: {message}')


def message_printer():
    while MESSAGING:
        os.system("cls")
        print(*MESSAGES[CURRENT_MESSENGER], sep="\n")
        time.sleep(1)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    service_setup(HOST, PORT, s)
    with socks.socksocket() as ss:
        ss.connect((f"{SERVER_ADDRESS}.onion", 5050))
        register = input("Do you want to register? y/n\n")
        while register != "n":
            if register != "y":
                print("Select y or n")
                continue
            nick = input("nick (can't contain white spaces): ")
            while " " in nick:
                nick = input("nick (CAN'T CONTAIN WHITE SPACES): ")
            address = open(f"{SERVICE_DIR}/hostname", "r").read().strip()
            ss.sendall(f"NEW {nick} {address[:-6]}\n".encode())
            res = read_data(ss)
            print(res.strip())
            if res.strip() == "registered":
                break
            input("Do you want to register? y/n")
        ss.sendall("GET\n".encode())
        users = json.loads(read_data(ss))
        for user in users:
            print(user)
    # TODO: implement connecting to others
    # TODO: implement saving nicks
    while True:
        # THIS ONLY ACCEPTS INCOMING MESSAGES - IMPLEMENT SENDING AND DISPLAYING THEM
        c, _ = s.accept()
        m = read_data(c)
        start_new_thread(messages_receiver, (c, m))
