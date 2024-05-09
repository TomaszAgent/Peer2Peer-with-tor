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
chats = {}

# Locks
LOCK = threading.Lock()

def clean_terminal():
    """
    This function is responsible for cleaning the terminal.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def messages_receiver(messenger: str):
    """
    This function is responsible for receiving messages from the server and other clients.
    """
    global running        

    while running:
        messenger_socket = chats[messenger]["socket"]
        message = read_data(messenger_socket)

        if message == "/CHAT CLOSE":
            # TODO: If user is in chat with that user move user to main menu (AKA choose_option)
            messenger_socket.close()
            with LOCK:
                chats.pop(messenger)
            return

        with LOCK:
            chats[messenger]["messages"].append(f"{messenger}: {message}")


def close_app(server_response: str | None = None) -> None:
    """
    This function is responsible for safely closing the application.
    """
    global running

    with LOCK:
        running = False
    # os.system("cls")
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
        connection.sendall("/CHAT CLOSE\n".encode())
        connection.close()

    quit()


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
    global current_messenger

    clean_terminal()
    click.echo("Loading users...")
    users = get_users()
    clean_terminal()
    click.echo("Select a user to start chat with")

    for user in users:
        if user == nick:
            continue
        click.echo(f"- {user}")

    chosen_user_nick = click.prompt("Type nickname", type=str)

    if chosen_user_nick == nick:
        clean_terminal()
        click.secho("You can't chat with yourself", fg="red")
        return

    if chosen_user_nick not in users:
        clean_terminal()
        click.secho("Invalid choice", fg="red")
        return

    chosen_user = users[chosen_user_nick]

    clean_terminal()

    socket_connection = socks.socksocket()
    click.echo(f"Connecting to {chosen_user[0]} on port {chosen_user[1]}...")
    socket_connection.connect((f"{chosen_user[0]}.onion", int(chosen_user[1])))
        
    socket_connection.sendall(f"NEW {nick} {ADDRESS[:-6]} {PORT}\n".encode())

    with LOCK:
        chats[chosen_user_nick] = {
            "messages": [],
            "socket": socket_connection,
            "address": chosen_user[0],
            "port": chosen_user[1]
        }

    # Create new thread for receiving messages
    messages_receiver_thread = threading.Thread(target=messages_receiver, args=(chosen_user_nick,), daemon=True)
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
    socket = chats[current_messenger]["socket"]

    if message == "/CHAT CLOSE":
        socket.sendall("/CHAT CLOSE\n".encode())

        with LOCK:
            chats.pop(current_messenger)
            messaging = False
        return
    socket.sendall((message + "\n").encode())

    with LOCK:
        chats[current_messenger]["messages"].append(f'{nick}: {message}')
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
        clean_terminal()
        click.echo(f"Chatting with {current_messenger}\n")
        print(*chats[current_messenger]["messages"], sep="\n")

        click.echo("\n[1] Write message")
        click.echo("[2] Close chat")
        time.sleep(0.1)


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
    
    with LOCK:
        current_messenger = chat_choice

    chat()



def user_options() -> None:
    """
    This function is responsible for handling user options.
    """
    global messaging

    while True:
        while messaging:
            pass
        clean_terminal()
        click.echo("What do you want to do?")
        click.echo("[1] Start a chat")
        click.echo("[2] Your chats")
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

            with LOCK:
                chats[nick] = {
                    "messages": [],
                    "socket": c,
                    "address": addr,
                    "port": port
                }

            # Create new thread for receiving messages
            messages_receiver_thread = threading.Thread(target=messages_receiver, args=(nick,), daemon=True)
            messages_receiver_thread.start()
        except Exception as e:
            print(e)


def register() -> None:
    """
    This function is responsible for registering the client with the server.
    """
    global nick

    with socks.socksocket() as server_socket:
        server_socket.connect((f"{SERVER_ADDRESS}.onion", 5050))

        print("im here")

        clean_terminal()
        with LOCK:
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

            # Create new thread for handling new connections
            new_connection_thread = threading.Thread(target=new_connection, daemon=True)
            new_connection_thread.start()

            user_options()
    except KeyboardInterrupt:
        close_app()
    except Exception as e:
        print(e)
        close_app()
