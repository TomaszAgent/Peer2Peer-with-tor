import configparser
import os

import click

_APP_PATH = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
_CONFIG_FILE_PATH = f"{_APP_PATH}/config.ini"


def get_hidden_service_address() -> str:
    return open(f"{_APP_PATH}/hidden_service/hostname", "r").read().strip()[:-6]

def _create_default_config():
    if not os.path.exists(_CONFIG_FILE_PATH):
        config = configparser.ConfigParser()
        config["Server"] = {
            "SERVER_ADDRESS": "",
            "SERVER_PORT": "",
        }
        config["Host"] = {
            "HOST": "127.0.0.1",
            "PORT": "5050",
        }

        with open(_CONFIG_FILE_PATH, "w") as configfile:
            config.write(configfile)
    else:
        click.echo(f"Config file already exists at {_CONFIG_FILE_PATH}")


def load_config() -> tuple[str, int, str, int] | None:
    """
    Loads the configuration from the config file

    Returns:
        SERVER INFO (tuple): The server address and port
        HIDDEN SERVICE ADDRESS (str): The hidden service address of the client
        HOST (str): The host address of the client
        PORT (int): The port of the client to listen on
    """
    if not os.path.exists(_CONFIG_FILE_PATH):
        _create_default_config()
        click.echo(f"Config file not found at {_CONFIG_FILE_PATH}. Creating a default config file")
        return
    
    config = configparser.ConfigParser()
    config.read(_CONFIG_FILE_PATH)

    server_address = config["Server"]["SERVER_ADDRESS"]
    server_port = int(config["Server"]["SERVER_PORT"])
    host = config["Host"]["HOST"]
    port = int(config["Host"]["PORT"])

    return (server_address, server_port), host, port


def load_hidden_services() -> list[tuple[str, str]]:
    """
    Loads all the hidden services from the hidden_services file

    Returns:
        LIST: List of all the hidden services in this format:
            [
                "HiddenServiceDir": "path/to/hidden_service_1_dir",
                "HiddenServicePort": "port1 host1:port1",
                "HiddenServiceDir": "path/to/hidden_service_2_dir",
                "HiddenServicePort": "port2 host2:port2",
            ]
    """

    config = configparser.ConfigParser()
    config.read(_CONFIG_FILE_PATH)

    hidden_services = []

    for section, options in config.items():
        if section.startswith("HiddenService"):
            service_dir = options.get("HiddenServiceDir")
            service_port = options.get("HiddenServicePort")

            if service_dir and service_port:
                hidden_services.extend([("HiddenServiceDir", service_dir),("HiddenServicePort", service_port)])
            else:
                raise ValueError(f"Hidden service {section} is missing either HiddenServiceDir or HiddenServicePort")
            
    return hidden_services