import socket
import time
import threading
import sys

import click
import socks
from halo import Halo
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from _config import HOST, PORT, SERVER_INFO, HIDDEN_SERVICE_ADDRESS
from helpers import clean_terminal, get_users, select_user, display_chat
from security import rsa_keypair, encrypt, decrypt, sign, verify
from connection import read_data, service_setup


socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150, True)

PRIVATE_KEY, PUBLIC_KEY = rsa_keypair()
PUBLIC_KEY_BYTES = PUBLIC_KEY.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

connected = False
messaging = False
chatting = False
running = True
nick = None
current_messenger = None
chats = {}

LOCK = threading.Lock()


def close_chat(socket, messenger: str) -> None:
    """
    This function is responsible for closing a chat.
    """
    global chats

    with LOCK:
        chats[messenger]["manage"]["running"] = False
        encrypted_message = encrypt("/CHAT CLOSE", chats[messenger]["info"]["public_key"])
        socket.sendall(encrypted_message + b"\n\n")
    chats[messenger]["manage"]["thread"].join()


# Application functions

def close_app(server_response: str | None = None) -> None:
    """
    This function is responsible for safely closing the application.
    """
    global running

    with LOCK:
        running = False

    if server_response:
        click.echo(f"Server response: {server_response.strip()}")
        click.secho("There was an error while registering. Exiting application.", fg="red")

    click.echo("Exiting application")

    if connected:
        server_socket = socks.socksocket()
        server_socket.connect(SERVER_INFO)
        server_socket.sendall(f"CLOSE {nick}\n\n".encode())
        server_socket.close()

        for messenger in list(chats):
            close_chat(chats[messenger]["info"]["socket"], messenger)

    sys.exit()


def messages_receiver(messenger: str):
    """
    This function is responsible for receiving messages from the server and other clients.
    """
    global chatting, chats

    while chats[messenger]["manage"]["running"]:
        messenger_socket = chats[messenger]["info"]["socket"]

        encrypted_message = read_data(messenger_socket, return_bytes=True)
        decrypted_message = decrypt(encrypted_message, PRIVATE_KEY)

        if decrypted_message == "/CHAT CLOSE":
            if chatting:
                with LOCK:
                    chatting = False
                click.echo(f"{messenger} has left the chat")

            encrypted_message = encrypt("/CHAT CLOSE2", chats[messenger]["info"]["public_key"])
            messenger_socket.sendall(encrypted_message + b"\n\n")
            with LOCK:
                chats.pop(messenger)
            messenger_socket.close()
            return

        if decrypted_message == "/CHAT CLOSE2":
            if chatting:
                chatting = False
                click.echo(f"{messenger} has left the chat")

            with LOCK:
                chats.pop(messenger)
                messenger_socket.close()
            return

        with LOCK:
            chats[messenger]["messages"].append(f"{messenger}: {decrypted_message}")


@Halo(text="Connecting to user", spinner="dots")
def connect_to_user(addr: str, port: int, user_public_key: rsa.RSAPublicKey) -> socket.socket | None:
    """
    Connect to the selected user and establish secure connection.
    """
    socket_conn = socks.socksocket()
    socket_conn.connect((f"{addr}.onion", port))

    signature = sign(nick.encode(), PRIVATE_KEY)

    encryped_message = encrypt(f"NEW {nick} {HIDDEN_SERVICE_ADDRESS} {PORT}", user_public_key)

    socket_conn.sendall(PUBLIC_KEY_BYTES + b"\n\n")
    time.sleep(0.5)
    socket_conn.sendall(signature + b"\n\n")
    time.sleep(0.5)
    socket_conn.sendall(encryped_message + b"\n\n")

    response = read_data(socket_conn)

    if response != "Connection Accepted":
        click.echo(response)
        click.echo("Connection refused")
        socket_conn.close()
        return
    return socket_conn


def start_chat() -> None:
    """
    This function is responsible for starting a chat with another user.
    """
    global current_messenger

    clean_terminal()
    users = get_users(SERVER_INFO)

    if not users:
        click.echo("No users available")
        return
    
    clean_terminal()
    click.echo("Select a user to start chat with")

    users.pop(nick)
    chosen_user_nick = select_user(users)
    if not chosen_user_nick:
        return
    
    clean_terminal()

    messenger_addr, messenger_port, messenger_public_key = users[chosen_user_nick]
    messenger_public_key = serialization.load_pem_public_key(messenger_public_key.encode())

    socket_conn = connect_to_user(messenger_addr, int(messenger_port), messenger_public_key)
    if not socket_conn:
        return
    
    messages_receiver_thread = threading.Thread(target=messages_receiver, args=(chosen_user_nick,), daemon=True)

    with LOCK:
        chats[chosen_user_nick] = {
            "messages": [],
            "info": {
                "socket": socket_conn,
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
    global current_messenger, messaging, chats

    with LOCK:
        messaging = True

    clean_terminal()

    message = click.prompt("Write message")
    socket = chats[current_messenger]["info"]["socket"]


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
    global current_messenger, chatting

    user_choice = click.getchar()

    if not chatting or messaging:
        return

    match user_choice:
        case "1":
            clean_terminal()
            write_message()
        case "2":
            messenger = current_messenger
            with LOCK:
                current_messenger = None
                chatting = False
            clean_terminal()
            
            closing_spinner = Halo(text="Closing chat", spinner="dots", placement="right")
            closing_spinner.start()
            close_chat(chats[messenger]["info"]["socket"], messenger)
            closing_spinner.stop_and_persist(text="Chat closed")

        case "3":
            clean_terminal()
            with LOCK:
                current_messenger = None
                chatting = False


def chat() -> None:
    """
    This function is responsible for handling the chat.
    """
    global chatting

    with LOCK:
        chatting = True

    chat_options_thread = threading.Thread(target=chat_options)
    chat_options_thread.start()

    while current_messenger and not messaging and chatting:
        display_chat(current_messenger, chats[current_messenger]["messages"])
        time.sleep(1)


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
    for nickname in list(chats):
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

        clean_terminal()

        options = {
            '1': ('Start a chat', start_chat),
            '2': ('Your chats', choose_chat),
            '3': ('Quit', close_app),
        }

        click.echo("Select an option")

        for key, (message, _) in options.items():
            click.echo(f'[{key}] {message}')

        user_choice = click.getchar()

        if chatting or messaging:
            continue

        if user_choice in options:
            _, action = options[user_choice]
            action()
        else:
            click.echo("Invalid choice")


def new_connection(s) -> None:
    """
    This function is responsible for handling new connections.
    """
    global running

    while running:
        socket, addr = s.accept()
        click.echo(f"New connection from {addr}")
        messenger_public_key = read_data(socket)

        messenger_public_key = serialization.load_pem_public_key(messenger_public_key.encode())

        signature = read_data(socket)

        encrypted_message = read_data(socket, return_bytes=True)

        try:
            decrypted_message = decrypt(encrypted_message, PRIVATE_KEY)
        except Exception as e:
            click.secho("There was problem while decrypting the message in the new connection", fg="red")
            click.echo(e)
            continue

        request, nick, addr, port = decrypted_message.split()

        if not verify(nick.encode(), signature, messenger_public_key):
            socket.sendall("Invalid signature\n\n".encode())
            socket.close()
            continue
        elif request != "NEW":
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
                    "public_key": messenger_public_key,
                },
                "manage": {
                    "running": True,
                    "thread": messages_receiver_thread
                }
            }

        messages_receiver_thread.start()


def register() -> None:
    """
    This function is responsible for registering the client with the server.
    """
    global nick, connected

    with socks.socksocket() as server_socket:
        connecting_spinner = Halo(text="Connecting to server", spinner="dots", placement="right")
        connecting_spinner.start()
        server_socket.connect(SERVER_INFO)
        connecting_spinner.stop_and_persist(text="Connected to server")

        with LOCK:
            nick = click.prompt("Enter your nickname").replace(" ", "_")

        register_spinner = Halo(text="Registering", spinner="dots", placement="right")
        register_spinner.start()
        register_message = f"NEW {nick} {HIDDEN_SERVICE_ADDRESS} {PORT} ".encode()
        server_socket.sendall(register_message + PUBLIC_KEY_BYTES + b"\n\n")

        res = read_data(server_socket)
        register_spinner.stop_and_persist(text="Successfully registered")

        if res == "User successfully registered":
            with LOCK:
                connected = True
            return
        else:
            close_app(server_response=res)


def main():
    """
    Main function to start the client application.

    This function initializes the socket, sets up the service with the specified host and port, registers the client, starts a new connection thread, and handles user options.
    """
    if not any([HOST, PORT, SERVER_INFO, HIDDEN_SERVICE_ADDRESS]):
        click.secho("Missing variables in config", fg="red")
        sys.exit()

    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    service_setup(HOST, PORT, socket)
    register()

    new_connection_thread = threading.Thread(target=new_connection, args=(socket,), daemon=True)
    new_connection_thread.start()

    user_options()


if __name__ == "_`_main__":
    try:
        main()
    except KeyboardInterrupt:
        close_app()
    except Exception as e:
        print(e)
        close_app()
