import socket
import socks
# from _thread import start_new_thread
import threading
from shared import read_data, service_setup
import json
import os
import time
import click

from rich.prompt import Prompt

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150, True)
HOST = "127.0.0.1"
PORT = 5025
# CURRENT_MESSENGER = "other nick"
# USER_NICK = "my nick"
SERVER_ADDRESS = "sjzh5pttbc2sqw3rwhcfistokg66ixn5h7lf3ckvgknuwby77723flad"
SERVICE_DIR = os.getcwd().replace("\\", "/") + "/src/client_second"
MESSAGING = False
RUNNING = True
new_message = False
NEW_MESSAGE_LOCK = threading.Lock()
chats = {}
CHATS_LOCK = threading.Lock()

def messages_receiver():
    while True:
        for messenger in chats:
            with CHATS_LOCK:
                messenger_socket = chats[messenger]["socket"]
                if message := read_data(messenger_socket):
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

def close_app():
    with socks.socksocket() as ss:
        ss.connect((f"{SERVER_ADDRESS}.onion", 5050))
        ss.sendall(f"CLOSE {nick}\n".encode())
        ss.close()

    # TODO implement closing all connections (imo sending a message to all users to close the connection)
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
    users = get_users()
    click.echo("Select a user to chat with")
    for user in users:
        if user == nick:
            continue
        click.echo(f"- {user}")

    chosen_user_nick = click.prompt("Type nickname", type=str)
    chosen_user = users[chosen_user_nick]

    with socks.socksocket() as socket_connection:
        click.echo(f"Connecting to {chosen_user[0]} on port {chosen_user[1]}...")
        socket_connection.connect((f"{chosen_user[0]}.onion", int(chosen_user[1])))

        socket_connection.sendall(f"NEW {nick} {address} {PORT}\n".encode())
        
        chats[chosen_user_nick] = {
            "messages": [],
            "socket": socket_connection,
            "address": chosen_user[0],
            "port": chosen_user[1]
        }

        click.echo("Chat started")

        return
    

def choose_chat():
    click.echo("Select a chat")
    if not chats:
        return "No chats available"
    for nickname in chats.keys():
        click.echo(f"- {nickname}")
    chat_choice = click.prompt("Type nickname", type=str)
    if chat_choice not in chats:
        click.secho("Invalid choice", fg="red")
        return
    print(chats[chat_choice]["messages"])


def user_options():
    global RUNNING
    click.echo("What do you want to do?")
    click.echo("[1] Start a chat")
    click.echo("[2] Your chats (new messages)" if new_message else "[2] Your chats")
    click.echo("[3] Quit")

    match click.getchar():
        case '1':
            click.echo("Starting a chat")
            start_chat()
        case '2':
            choose_chat()
            return
        case '3':
            click.echo("Exiting application")
            RUNNING = False
            close_app()
        case _:
            click.echo("Invalid choice")
            return
        

def new_connection():
    while True:        
        try:
            c, addr = s.accept()
            click.echo(f"New connection from {addr}")
            m = read_data(c)
            chats[m] = {
                "messages": [],
                "socket": c,
                "address": addr
            }
        except Exception as e:
            print(e)

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        service_setup(HOST, PORT, s)
        with socks.socksocket() as ss:
            ss.connect((f"{SERVER_ADDRESS}.onion", 5050))

            # Registering
            click.echo("Do you want to register? [y/n] ", nl=False)
            register = click.getchar()
            click.echo()

            if register == 'y':
                nick = click.prompt("Enter your nickname").replace(" ", "_")

                address = open(os.getcwd().replace("\\", "/") + "/src/hidden_services/clients/client2/hostname", "r").read().strip()
                ss.sendall(f"NEW {nick} {address[:-6]} {PORT}\n".encode())
                res = read_data(ss)

                # TODO: Implement handling server responses for registration
                if res.strip() != "registered":
                    click.echo(f"Server response: {res.strip()}")
                    click.secho("There was an error while registering. Exiting application.", fg="red")
                    close_app()
            else:
                click.echo("Exiting application")
                close_app()
            ss.sendall("GET\n".encode())
            users = json.loads(read_data(ss))

            click.echo()

            click.secho("Users:", bold=True)
            for idx, user in enumerate(users):
                print(f"{idx+1}. {user}")

        # TODO: implement connecting to others
        # TODO: implement saving nicks
        new_connection_thread = threading.Thread(target=new_connection, daemon=True)
        messages_receiver_thread = threading.Thread(target=messages_receiver, daemon=True)
        new_connection_thread.start()
        messages_receiver_thread.start()
        while RUNNING:
            user_options()
            # THIS ONLY ACCEPTS INCOMING MESSAGES - IMPLEMENT SENDING AND DISPLAYING THEM
except KeyboardInterrupt:
    close_app()
except Exception as e:
    print(e)
    close_app()