import sys
import json
import socket
import time
from _thread import start_new_thread

import click
from cryptography.hazmat.primitives import serialization

from config import load_config
from connection import read_data, send_response, service_setup
from helpers import clean_terminal


users = {}
HOST, PORT = load_config()
print(HOST, PORT)


def handle_requests(client_socket: socket.socket, message: str) -> None:
    """
    This function is responsible for handling requests from the client that are not related to registering a user.
    """
    match message.split()[0]:
        case "NEW":
            register_user(client_socket, message)
        case "GET":
            users_list = json.dumps(users)
            send_response(client_socket, users_list)
        case "CLOSE":
            nick = message.split()[1]
            users.pop(nick)
            client_socket.close()
        case _:
            send_response(client_socket, "Invalid request")

    
def register_user(client_socket: socket.socket, message: str) -> None:
    """
    This function is responsible for registering a new user.
    """    
    message = message.split(maxsplit=4)

    if len(message) == 5:
        _, nick, address, port, user_public_key = message

        try: 
            serialization.load_pem_public_key(user_public_key.encode())
        except ValueError:
            send_response(client_socket, "Public key is invalid")

        if not address.isalnum() or len(address) != 56:            
            send_response(client_socket, "Address is invalid")
        elif address in [user[0] for user in users.values()]:
            send_response(client_socket, "Address is taken")
        elif nick in users.keys():
            send_response(client_socket, "Nick is taken")
        else:
            users[nick] = (address, port, user_public_key)
            send_response(client_socket, "User successfully registered")
            return
    send_response(client_socket, "Invalid registration request")
    return


def connection_handler(client_socket: socket.socket) -> None:
    """
    This function is responsible for handling a connection with a client.
    """   
    while True: 
        message = read_data(client_socket)
        handle_requests(client_socket, message)


def user_printer() -> None:
    """
    This function is reposible for printing the users connected to the server.
    """
    while True:
        clean_terminal()
        print(f"There is {len(users)} user(s) connected: ")
        for user in users:
            print(f"{user}: {users[user][0]}:{users[user][1]}")
        time.sleep(1)


def main():
    """
    Main function to start the server.

    It starts a new thread to print the users connected to the server and then listens for incoming connections.
    """
    if not all([HOST, PORT]):
        click.secho("[Configuration error] Missing variables in config", fg="red")
        click.echo("Click any key to close app")
        if click.getchar():
            sys.exit()

    start_new_thread(user_printer, ())
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        service_setup(HOST, PORT, server_socket)
        while True:
            client, _ = server_socket.accept()
            start_new_thread(connection_handler, (client,))


def run():
    try:
        main()
    except KeyboardInterrupt:
        click.echo("Shutting down server")
        click.echo("Click any key to close")
        if click.getchar():
            sys.exit()
    except Exception as e:
        click.secho(f"[Unexpected error] {e}", fg="red")
        click.echo("Click any key to close")
        if click.getchar():
            sys.exit()


if __name__ == "__main__":
    main()
