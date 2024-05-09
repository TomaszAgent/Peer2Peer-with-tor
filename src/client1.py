import json
import os
import socket
import time
import threading

import click
import socks
from shared import read_data, service_setup


socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150, True)
HOST = "127.0.0.1"
PORT = 5001
SERVER_ADDRESS = "yhpc3gkjqemsfpc4hcnfrvciil3xqgis4ipqfgootcgigawltlunxzqd"
ADDRESS = open(os.getcwd().replace("\\", "/") + "/src/hidden_services/clients/client1/hostname", "r").read().strip()
messaging = False
running = True
nick = None
connected = False
current_messenger = None
new_message = False
chats = {}

# Locks
NEW_MESSAGE_LOCK = threading.Lock()
CHATS_LOCK = threading.Lock()


def messages_receiver(messenger: str):
    """
    This function is responsible for receiving messages from the server and other clients.
    """
    global running, new_message        

    while running:
        with CHATS_LOCK:
            messenger_socket = chats[messenger]["socket"]
            message = read_data(messenger_socket)

            with NEW_MESSAGE_LOCK:
                new_message = True

            chats[messenger]["messages"].append(f"{messenger}: {message}")


# def messages_sender(c: socket.socket):
#     global MESSAGING
#     MESSAGING = True
#     while True:
#         message = input()
#         if message == "\\quit":
#             MESSAGING = False
#             break
#         c.sendall(message.encode())
#         chats[CURRENT_MESSENGER].append(f'You: {message}')


# def message_printer():
#     while MESSAGING:
#         os.system("cls")
#         print(*chats[CURRENT_MESSENGER], sep="\n")
#         time.sleep(1)

def close_app(server_response: str | None = None) -> None:
    """
    This function is responsible for safely closing the application.
    """
    global running

    running = False
    os.system("cls")
    if server_response is not None:
        click.echo(f"Server response: {server_response.strip()}")
        click.secho("There was an error while registering. Exiting application.", fg="red")
        quit()
    
    click.echo("Exiting application")
    with socks.socksocket() as server_socket:
        server_socket.connect((f"{SERVER_ADDRESS}.onion", 5050))
        server_socket.sendall(f"CLOSE {nick}\n".encode())
        server_socket.close()

    for connection in [chats[messenger]["socket"] for messenger in chats]:
        connection.sendall("\\close\n".encode())
        connection.close()

    quit()


def print_messages(messenger: str) -> None:
    """
    This function is responsible for printing messages from a specific chat.
    """
    os.system("cls")
    print(*chats[messenger]["messages"], sep="\n")


def get_users() -> dict:
    """
    This function is responsible for getting all users from the server.
    """
    with socks.socksocket() as server_socket:
        server_socket.connect((f"{SERVER_ADDRESS}.onion", 5050))
        server_socket.sendall("GET\n".encode())
        return json.loads(read_data(server_socket))
    

def start_chat() -> None:
    """
    This function is responsible for starting a chat with another user.
    """
    os.system("cls")
    click.echo("Loading users...")
    users = get_users()
    os.system("cls")
    click.echo("Select a user to start chat with")

    for user in users:
        if user == nick:
            continue
        click.echo(f"- {user}")

    chosen_user_nick = click.prompt("Type nickname", type=str)

    if chosen_user_nick not in users:
        os.system("cls")
        click.secho("Invalid choice", fg="red")
        return

    chosen_user = users[chosen_user_nick]

    socket_connection = socks.socksocket()
    click.echo(f"Connecting to {chosen_user[0]} on port {chosen_user[1]}...")
    socket_connection.connect((f"{chosen_user[0]}.onion", int(chosen_user[1])))
        
    socket_connection.sendall(f"NEW {nick} {ADDRESS[:-6]} {PORT}\n".encode())

    chats[chosen_user_nick] = {
        "messages": [],
        "socket": socket_connection,
        "address": chosen_user[0],
        "port": chosen_user[1]
    }

    click.echo("Chat started")

    return


def write_message() -> None:
    """
    This function is responsible for writing a message to a chat.
    """
    global current_messenger, messaging

    messaging = True
    os.system("cls")
    message = click.prompt("message")
    s = chats[current_messenger]["socket"]
    s.sendall((message + "\n").encode())
    chats[current_messenger]["messages"].append(f'{nick}: {message}')
    messaging = False


def chat_options() -> None:
    """
    This function is responsible for handling chat options.
    """
    global current_messenger

    match click.getchar():
        case "1":
            write_message()
        case "2":
            current_messenger = None


def choose_chat() -> None:
    """
    This function is responsible for choosing a chat.
    """
    global current_messenger
    
    os.system("cls")
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
    current_messenger = chat_choice
    chat_options_thread = threading.Thread(target=chat_options, daemon=True)
    chat_options_thread.start()
    while current_messenger and not messaging:
        os.system("cls")
        print("1 - write a message; 2 - quit")
        print(*chats[chat_choice]["messages"], sep="\n")
        time.sleep(1)



def user_options() -> None:
    """
    This function is responsible for handling user options.
    """
    global messaging
    while True:
        while messaging:
            pass
        os.system("cls")
        click.echo("What do you want to do?")
        click.echo("[1] Start a chat")
        click.echo("[2] Your chats (new messages)" if new_message else "[2] Your chats")
        click.echo("[3] Quit")

        match click.getchar():
            case '1':
                start_chat()
            case '2':
                choose_chat()
            case '3':
                close_app()
            case _:
                click.echo("Invalid choice")


def new_connection()-> None:
    """
    This function is responsible for handling new connections.
    """
    global running

    while running:
        try:
            c, addr = s.accept()
            click.echo(f"New connection from {addr}")
            m = read_data(c)
            _, nick, addr, port = m.split()
            chats[nick] = {
                "messages": [],
                "socket": c,
                "address": addr,
                "port": port
            }
        except Exception as e:
            print(e)


def register() -> None:
    """
    This function is responsible for registering the client with the server.
    """
    global nick

    with socks.socksocket() as server_socket:
        server_socket.connect((f"{SERVER_ADDRESS}.onion", 5050))

        os.system("cls")
        nick = click.prompt("Enter your nickname").replace(" ", "_")
        server_socket.sendall(f"NEW {nick} {ADDRESS[:-6]} {PORT}\n".encode())
        res = read_data(server_socket)

        # TODO: Implement handling server responses for registration
        if res.strip() != "registered":
            close_app(server_response=res)


if __name__ == "__main__":
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            service_setup(HOST, PORT, s)
            register()
            new_connection_thread = threading.Thread(target=new_connection, daemon=True)
            messages_receiver_thread = threading.Thread(target=messages_receiver, daemon=True)
            new_connection_thread.start()
            messages_receiver_thread.start()
            user_options()
    except KeyboardInterrupt:
        close_app()
    except Exception as e:
        print(e)
        close_app()
