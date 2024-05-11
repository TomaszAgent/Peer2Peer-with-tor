import json
import os
import socket
import time
import threading

import click
import halo
import socks
from cryptography.hazmat.primitives import serialization

from shared import *


socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150, True)
HOST = "127.0.0.1"
PORT = 5025
SERVER_ADDRESS = "yhpc3gkjqemsfpc4hcnfrvciil3xqgis4ipqfgootcgigawltlunxzqd"
ADDRESS = open(os.getcwd().replace("\\", "/") + "/src/hidden_services/clients/client2/hostname", "r").read().strip()
server_public_key = None
server_socket = None
connected = False
messaging = False
running = True
nick = None
current_messenger = None
chats = {}

# Locks
LOCK = threading.Lock()

PRIVATE_KEY, PUBLIC_KEY = rsa_keypair()
PUBLIC_KEY_BYTES = PUBLIC_KEY.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)


# Application functions

def close_app(server_response: str | None = None) -> None:
    """
    This function is responsible for safely closing the application.
    """
    global running

    with LOCK:
        running = False

    if server_response is not None:
        click.echo(f"Server response: {server_response.strip()}")
        click.secho("There was an error while registering. Exiting application.", fg="red")
        quit()
    
    click.echo("Exiting application")

    # TODO: Implement decrypting the message
    if connected:
        with socks.socksocket() as server_socket:
            server_socket.connect((f"{SERVER_ADDRESS}.onion", 5050))
            server_socket.sendall(f"CLOSE {nick}\n\n".encode())
            server_socket.close()

        for connection in [chats[messenger]["info"]["socket"] for messenger in chats]:
            connection.sendall("/CHAT CLOSE\n\n".encode())
            connection.close()

    quit()


# Server functions

def get_users() -> dict[str]:
    """
    This function is responsible for getting all users from the server.
    """
    click.echo("Loading users...")
    with socks.socksocket() as server_socket: 
        server_socket.connect((f"{SERVER_ADDRESS}.onion", 5050))
        server_socket.sendall("GET".encode() + b"\n\n")

        res = read_data(server_socket)

        return json.loads(res)
    

# Chat functions

def messages_receiver(messenger: str):
    """
    This function is responsible for receiving messages from the server and other clients.
    """  
    while chats[messenger]["manage"]["running"]:
        messenger_socket = chats[messenger]["info"]["socket"]

        encrypted_message = read_data(messenger_socket, return_bytes=True)
        decrypted_message = decrypt(encrypted_message, PRIVATE_KEY)

        if decrypted_message == "/CHAT CLOSE":
            # TODO: If user is in chat with that user move user to main menu (AKA choose_option)
            messenger_socket.close()
            with LOCK:
                chats.pop(messenger)
            return

        with LOCK:
            chats[messenger]["messages"].append(f"{messenger}: {decrypted_message}")

    
def start_chat() -> None:
    """
    This function is responsible for starting a chat with another user.
    """
    global current_messenger

    clean_terminal()
    users = get_users()
    clean_terminal()
    click.echo("Select a user to start chat with")

    users.pop(nick)
    for user in users:
        click.echo(f"- {user}")

    chosen_user_nick = click.prompt("Type nickname", type=str)

    if chosen_user_nick not in users:
        clean_terminal()
        click.secho("Invalid choice", fg="red")
        return

    clean_terminal()

    messenger_addr, messenger_port, messenger_public_key = users[chosen_user_nick]
    messenger_public_key = serialization.load_pem_public_key(messenger_public_key.encode())

    click.echo(f"Connecting to {messenger_addr} on port {messenger_port}...")
    socket_connection = socks.socksocket()
    socket_connection.connect((f"{messenger_addr}.onion", int(messenger_port)))    
    
    signature = sign(nick.encode(), PRIVATE_KEY)
    print(signature)

    encryped_message = encrypt(f"NEW {nick} {ADDRESS[:-6]} {PORT}", messenger_public_key)
    
    socket_connection.sendall(PUBLIC_KEY_BYTES + b"\n\n")
    time.sleep(0.5)
    socket_connection.sendall(signature + b"\n\n")
    time.sleep(0.5)
    socket_connection.sendall(encryped_message + b"\n\n")

    response = read_data(socket_connection)

    if response != "Connection Accepted":
        click.echo(response)
        click.echo("Connection refused")
        socket_connection.close()
        return

    messages_receiver_thread = threading.Thread(target=messages_receiver, args=(chosen_user_nick,))

    with LOCK:
        chats[chosen_user_nick] = {
            "messages": [],
            "info": {
                "socket": socket_connection,
                "address": messenger_addr,
                "port": messenger_port,
                "public_key": messenger_public_key
            },
            "manage": {
                "running": True,
                "thread": messages_receiver_thread
            }
        }

    messages_receiver_thread.start()

    click.echo("Chat started")

    with LOCK:
        current_messenger = chosen_user_nick

    chat()



def write_message() -> None:
    """
    This function is responsible for writing a message to a chat.
    """
    global current_messenger, messaging

    with LOCK:
        messaging = True

    clean_terminal()

    message = click.prompt("Write message")
    socket = chats[current_messenger]["info"]["socket"]

    if message == "/CHAT CLOSE":
        with LOCK:
            chats[current_messenger]["manage"]["running"] = False
            chats[current_messenger]["manage"]["thread"].join()
            chats.pop(current_messenger)
            current_messenger = None
            # ! encrypt this wtf?
            socket.sendall(message.encode() + b"\n\n")

    else:
        with LOCK:
            chats[current_messenger]["messages"].append(f'{nick}: {message}')

    encrypted_message = encrypt(message, chats[current_messenger]["info"]["public_key"])
    socket.sendall(encrypted_message + b"\n\n")

    with LOCK:
        messaging = False

    chat()


def chat_options() -> None:
    """
    This function is responsible for handling chat options.
    """
    global current_messenger

    match click.getchar():
        case "1":
            write_message()
        case "2":
            with LOCK:
                current_messenger = None


def chat() -> None:
    chat_options_thread = threading.Thread(target=chat_options, daemon=True)
    chat_options_thread.start()
    while current_messenger and not messaging:
        # clean_terminal()
        click.echo(f"Chatting with {current_messenger}\n")
        print(*chats[current_messenger]["messages"], sep="\n")

        click.echo("\n[1] Write message")
        click.echo("[2] Close chat")
        time.sleep(0.5)


def choose_chat() -> None:
    """
    This function is responsible for choosing a chat.
    """
    global current_messenger
    
    clean_terminal()
    click.echo("Select a chat")

    if not chats:
        click.echo("No chats available")
        return
    for nickname in chats.keys():
        click.echo(f"- {nickname}")

    chat_choice = click.prompt("Type nickname", type=str)

    if chat_choice not in chats:
        click.secho("Invalid choice", fg="red")
        return
    else:    
        with LOCK:
            current_messenger = chat_choice
        chat()


def user_options() -> None:
    """
    This function is responsible for handling user options.
    """
    while True:
        while messaging:
            pass

        options = {
            '1': ('Start a chat', start_chat),
            '2': ('Your chats', choose_chat),
            '3': ('Quit', close_app),
        }

        for key, (message, _) in options.items():
            click.echo(f'[{key}] {message}')

        user_choice = click.getchar()

        if user_choice in options:
            _, action = options[user_choice]
            action()
        else:
            click.echo("Invalid choice")


def new_connection()-> None:
    """
    This function is responsible for handling new connections.
    """
    global running

    while running:
        try:
            socket, addr = s.accept()
            click.echo(f"New connection from {addr}")
            messanger_public_key = read_data(socket)

            messanger_public_key = serialization.load_pem_public_key(messanger_public_key.encode())

            signature = read_data(socket)

            encrypted_message = read_data(socket, return_bytes=True)

            try:
                decrypted_message = decrypt(encrypted_message, PRIVATE_KEY)
            except Exception as e:
                click.secho("There was problem while decrypting the message in the new connection", fg="red")
                click.echo(e)
                continue

            request, nick, addr, port = decrypted_message.split()
            
            if not verify(nick.encode(), signature, messanger_public_key):
                socket.sendall("Invalid signature\n\n".encode())
                socket.close()
                continue

            if request != "NEW":
                socket.sendall("Invalid request\n\n".encode())
                socket.close()
                continue
            elif nick in chats:
                socket.sendall("There's already open chat\n\n".encode())
                socket.close()
                continue

            socket.sendall("Connection Accepted\n\n".encode())
            
            messages_receiver_thread = threading.Thread(target=messages_receiver, args=(nick,))

            with LOCK:
                chats[nick] = {
                    "messages": [],
                    "info": {
                        "socket": socket,
                        "address": addr,
                        "port": port,
                        "public_key": messanger_public_key,
                    },
                    "manage": {
                        "running": True,
                        "thread": messages_receiver_thread
                    }
                }

            messages_receiver_thread.start()
        except Exception as e:
            print(e)


def register() -> None:
    """
    This function is responsible for registering the client with the server.
    """
    global nick, server_public_key

    with socks.socksocket() as server_socket:
        print("Connecting to server...")
        server_socket.connect((f"{SERVER_ADDRESS}.onion", 5050))                

        click.echo("Connected to server\n")

        with LOCK:
            nick = click.prompt("Enter your nickname").replace(" ", "_")

        register_message = f"NEW {nick} {ADDRESS[:-6]} {PORT} ".encode()
        server_socket.sendall(register_message + PUBLIC_KEY_BYTES + b"\n\n")
        
        res = read_data(server_socket)

        if res == "User successfully registered":
            return
        else:
            close_app(server_response=res)


if __name__ == "__main__":
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            service_setup(HOST, PORT, s)
            register()

            # Create new thread for handling new connections
            new_connection_thread = threading.Thread(target=new_connection, daemon=True)
            new_connection_thread.start()

            user_options()
    except KeyboardInterrupt:
        close_app()
    except Exception as e:
        print(e)
        close_app()
