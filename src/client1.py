import socket
import time

import socks
import threading
from shared import read_data, service_setup
import json
import os
import click


socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150, True)
HOST = "127.0.0.1"
PORT = 5001
CURRENT_MESSENGER = None
USER_NICK = ""
SERVER_ADDRESS = "eyp6hesvb3y3gue2iwztuw2o4japnrfmmxonpleaafzfzxgskmq3dlid"
SERVICE_DIR = os.getcwd().replace("\\", "/") + "/src/client"
MESSAGING = False
RUNNING = True
connected = False
new_message = False
chats = {}
NEW_MESSAGE_LOCK = threading.Lock()
CHATS_LOCK = threading.Lock()


def messages_receiver():
    global RUNNING
    while RUNNING:
        for messenger in chats:
            with CHATS_LOCK:
                messenger_socket = chats[messenger]["socket"]
                message = read_data(messenger_socket)
                if message == "\\close":
                    chats.pop(messenger)
                    messenger_socket.close()
                with NEW_MESSAGE_LOCK:
                    global new_message
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

def close_app(server_response=None):
    global RUNNING
    RUNNING = False
    if server_response is not None:
        click.echo(f"Server response: {res.strip()}")
        click.secho("There was an error while registering. Exiting application.", fg="red")
        quit()
    os.system("cls")
    click.echo("Exiting application")
    with socks.socksocket() as ss:
        ss.connect((f"{SERVER_ADDRESS}.onion", 5050))
        ss.sendall(f"CLOSE {USER_NICK}\n".encode())
        ss.close()

    for connection in [chats[messenger]["socket"] for messenger in chats]:
        connection.sendall("\\close\n".encode())
        connection.close()

    quit()


def print_messages(messenger):
    os.system("cls")
    print(*chats[messenger]["messages"], sep="\n")


def get_users():
    with socks.socksocket() as ss:
        ss.connect((f"{SERVER_ADDRESS}.onion", 5050))
        ss.sendall("GET\n".encode())
        return json.loads(read_data(ss))
    

def start_chat():
    os.system("cls")
    click.echo("Loading users...")
    users = get_users()
    os.system("cls")
    click.echo("Select a user to start chat with")
    for user in users:
        if user == USER_NICK:
            continue
        click.echo(f"- {user}")

    chosen_user_nick = click.prompt("Type nickname", type=str)
    chosen_user = users[chosen_user_nick]

    socket_connection = socks.socksocket()
    click.echo(f"Connecting to {chosen_user[0]} on port {chosen_user[1]}...")
    socket_connection.connect((f"{chosen_user[0]}.onion", int(chosen_user[1])))
        
    socket_connection.sendall(f"NEW {USER_NICK} {address[:-6]} {PORT}\n".encode())

    chats[chosen_user_nick] = {
        "messages": [],
        "socket": socket_connection,
        "address": chosen_user[0],
        "port": chosen_user[1]
    }

    click.echo("Chat started")

    return


def write_message():
    global CURRENT_MESSENGER, MESSAGING
    MESSAGING = True
    os.system("cls")
    message = click.prompt("message")
    s = chats[CURRENT_MESSENGER]["socket"]
    s.sendall((message + "\n").encode())
    chats[CURRENT_MESSENGER]["messages"].append(f'{USER_NICK}')
    MESSAGING = False


def chat_options():
    global CURRENT_MESSENGER
    match click.getchar():
        case "1":
            write_message()
        case "2":
            CURRENT_MESSENGER = None


def choose_chat():
    global CURRENT_MESSENGER
    os.system("cls")
    click.echo("Select a chat")
    if not chats:
        return "No chats available"
    for nickname in chats.keys():
        click.echo(f"- {nickname}")
    chat_choice = click.prompt("Type nickname", type=str)
    if chat_choice not in chats:
        click.secho("Invalid choice", fg="red")
        return
    CURRENT_MESSENGER = chat_choice
    chat_options_thread = threading.Thread(target=chat_options, daemon=True)
    chat_options_thread.start()
    while CURRENT_MESSENGER and not MESSAGING:
        os.system("cls")
        print("1 - write a message; 2 - quit")
        print(*chats[chat_choice]["messages"], sep="\n")
        time.sleep(1)


def user_options():
    global MESSAGING
    while True:
        while MESSAGING:
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


def new_connection():
    global RUNNING
    while RUNNING:
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


try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        service_setup(HOST, PORT, s)
        with socks.socksocket() as ss:
            ss.connect((f"{SERVER_ADDRESS}.onion", 5050))

            os.system("cls")
            USER_NICK = click.prompt("Enter your nickname").replace(" ", "_")
            address = open(os.getcwd().replace("\\", "/") + "/src/hidden_services/clients/client1/hostname", "r").read().strip()
            ss.sendall(f"NEW {USER_NICK} {address[:-6]} {PORT}\n".encode())
            res = read_data(ss)

            # TODO: Implement handling server responses for registration
            if res.strip() != "registered":
                close_app(server_response=res.strip())

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
