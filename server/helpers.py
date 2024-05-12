import os


def clean_terminal():
    """
    This function is responsible for cleaning the terminal.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
