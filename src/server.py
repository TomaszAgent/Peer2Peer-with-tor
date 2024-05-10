import json
import socket
import time
from _thread import start_new_thread

import click
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from shared import *


HOST = "127.0.0.1"
PORT = 5050
PRIVATE_KEY, PUBLIC_KEY = rsa_keypair()
PUBLIC_KEY_BYTES = PUBLIC_KEY.public_bytes(
   encoding=serialization.Encoding.PEM,
   format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# TODO: Implement threading instead of _thread
# LOCK = threading.Lock()

users = {}


def send_response(client_socket: socket.socket, response: str, key: rsa.RSAPublicKey | None = None) -> None:
    """
    This function is responsible for sending a response to the client.
    """
    # ! This function can only encrypt text not longer than 190 bytes (RSA limitation)
    # TODO: Implement sending messages in chunks to avoid this limitation (this may change the protocol)
    if key:
        response = encrypt(response, key)
        print(response)
        client_socket.sendall(response + b"\n\n")
    else:
        client_socket.sendall(response.encode() + b"\n\n")


def handle_requests(client_socket: socket.socket, message: str, user_public_key: rsa.RSAPublicKey) -> None:
    """
    This function is responsible for handling requests from the client that are not related to registering a user.
    """
    match message.split()[0]:
        case "NEW":
            register_user(client_socket, message, user_public_key)
        case "GET_USERS":
            nicks_list = users.keys()
            send_response(client_socket, nicks_list, user_public_key)
        case "GET_USER":
            users_nick = message.split()[1]
            if user := users.get(users_nick):
                send_response(
                    client_socket, f"{user[0]} {user[1]}", user_public_key
                )
            else:
                send_response(client_socket, "User not found", user_public_key)
        case "CLOSE":
            nick = message.split()[1]
            users.pop(nick)
            client_socket.close()
        case _:
            send_response(client_socket, "Invalid request", user_public_key)

    
def register_user(client_socket: socket.socket, message: str, user_public_key: rsa.RSAPublicKey) -> None:
    """
    This function is responsible for registering a new user.
    """    
    message = message.split()

    if len(message) == 4:
        _, nick, address, port = message

        if not address.isalnum() or len(address) != 56:            
            send_response(client_socket, "Address is invalid", user_public_key)
        elif address in [user[0] for user in users.values()]:
            send_response(client_socket, "Address is taken", user_public_key)
        elif nick in users.keys():
            send_response(client_socket, "Nick is taken", user_public_key)
        else:
            user_public_key_bytes = user_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            users[nick] = (address, port, user_public_key_bytes.decode())
            send_response(client_socket, "User successfully registered", user_public_key)
            return
    send_response(client_socket, "Invalid registration request", user_public_key)
    return


def connection_handler(client_socket: socket.socket) -> None:
    """
    This function is responsible for handling a connection with a client.
    """
    click.echo(f"New connection from {client_socket.getpeername()}")
    time.sleep(1)
    client_socket.sendall(PUBLIC_KEY_BYTES + b"\n\n")
    click.echo(f"Public key sent to {client_socket.getpeername()}")

    users_public_key = read_data(client_socket)

    try:
        users_public_key = serialization.load_pem_public_key(users_public_key.encode())
    except ValueError:
        print(users_public_key)
        send_response(client_socket, "Invalid public key")
        return
    
    send_response(client_socket, "Public key received")
    click.echo(f"Public key received from {client_socket.getpeername()}")

    while True:
        message = read_data(client_socket, return_bytes=True)
        click.echo(f"Received message from {client_socket.getpeername()}: {message}")

        print(message)
        try:
            decrypted_message = decrypt(message[1:], PRIVATE_KEY)
        except ValueError:
            decrypted_message = decrypt(message, PRIVATE_KEY)

        handle_requests(client_socket, decrypted_message, users_public_key)


def user_printer() -> None:
    """
    This function is reposible for printing the users connected to the server.
    """
    while True:
        # clean_terminal()
        # print(f"There is {len(users)} user(s) connected: ")
        # for user in users:
        #     print(f"{user}: {users[user]}")
        time.sleep(1)


if __name__ == "__main__":
    start_new_thread(user_printer, ())
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        service_setup(HOST, PORT, server_socket)
        while True:
            client, _ = server_socket.accept()
            start_new_thread(connection_handler, (client,))
