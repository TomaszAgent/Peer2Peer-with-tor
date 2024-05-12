import os
import json
import socks

import click
from halo import Halo
from connection import read_data


def clean_terminal():
    """
    This function is responsible for cleaning the terminal.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def display_chat(messenger: str, messages: list[str]) -> None:
    """
    This function is responsible for displaying chat messages.
    """
    clean_terminal()
    click.echo(f"Chatting with {messenger}\n")
    print(*messages, sep="\n")

    click.echo("\n[1] Write message")
    click.echo("[2] Close chat")
    click.echo("[3] Go back to main menu\n")


@Halo(text="Loading users", spinner="dots")
def get_users(server_info: tuple[str, int]) -> dict[str]:
    """
    This function is responsible for getting all users from the server.
    """
    with socks.socksocket() as server_socket:
        server_socket.connect(server_info)
        server_socket.sendall("GET".encode() + b"\n\n")

        res = read_data(server_socket)
        
        return json.loads(res)
    

def select_user(users: dict) -> str | None:
    """
    This function is responsible for selecting a user to chat with.
    """
    clean_terminal()
    click.echo("Select a user to start chat with")
    
    for user in users:
        click.echo(f"- {user}")

    chosen_user_nick = click.prompt("Type nickname", type=str)

    if chosen_user_nick not in users:
        clean_terminal()
        click.secho("Invalid choice", fg="red")
        return None

    return chosen_user_nick
