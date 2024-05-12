import json
import socket
import time
from _thread import start_new_thread

from cryptography.hazmat.primitives import serialization

from _config import HOST, PORT
from helpers import clean_terminal
from connection import read_data, send_response, service_setup


users = {}

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
            # print(f"User {nick} registered with address {address} and port {port}")
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
    start_new_thread(user_printer, ())
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        service_setup(HOST, PORT, server_socket)
        while True:
            client, _ = server_socket.accept()
            start_new_thread(connection_handler, (client,))


if __name__ == "__main__":
    main()
