import socket
import socks
import os
from _thread import start_new_thread
from stem.control import Controller
from shared import read_data, service_setup

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150, True)
HOST = "127.0.0.1"
PORT = 5000
CURRENT_MESSENGER = "other nick"
USER_NICK = "my nick"


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
    # TODO: implement connection with server
    # TODO: implement connecting to others
    # TODO: implement receiving messages in the background
    # TODO: implement saving nicks and addresses
    while True:
        c, _ = s.accept()
        start_new_thread(messages_receiver, (c,))
        start_new_thread(messages_sender, (c,))
