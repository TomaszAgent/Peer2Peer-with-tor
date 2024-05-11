import os
import socket
import base64
from stem.control import Controller
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
import cryptography


PROJECT_PATH = os.getcwd().replace("\\", "/")

def encrypt(message: str, public_key: rsa.RSAPublicKey) -> bytes:
    """
    This function encrypts a message using the public key.
    """
    return public_key.encrypt(message.encode(), padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))


def decrypt(message: bytes, private_key: rsa.RSAPrivateKey) -> str:
    """
    This function decrypts a message using the private key.
    """
    return private_key.decrypt(message, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)).decode()


def rsa_keypair() -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    """
    This function generates a RSA key pair.
    """
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    return (private_key, private_key.public_key())


def sign(message: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
    """
    This function signs a message using the private key.
    """
    padding_instance = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)
    return base64.b64encode(private_key.sign(message, padding_instance, hashes.SHA256()))


def verify(message: bytes, signature: str, public_key: rsa.RSAPublicKey) -> bool:
    """
    This function verifies a signature using the public key.
    """
    sig = base64.b64decode(signature)
    padding_instance = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)
    try:
        public_key.verify(sig, message, padding_instance, hashes.SHA256())
        return True
    except cryptography.exceptions.InvalidSignature:
        return False
    

def read_data(client_socket: socket.socket, return_bytes = False) -> str | bytes:
    """
    Reads data from a socket. Function waits until message is completed using '\\n\\n' as a delimiter.
    """
    data = b''
    while b'\n\n' not in data:
        data += client_socket.recv(1)

    return data.replace(b'\n\n', b'') if return_bytes else data.decode().strip()


def clean_terminal():
    """
    This function is responsible for cleaning the terminal.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def service_setup(host: str, post: int, socket: socket.socket) -> None:
    """
    Set up a hidden service for the server and clients
    """
    socket.bind((host, post))
    socket.listen(5)
    controller = Controller.from_port(address="127.0.0.1", port=9151)
    controller.authenticate()
    controller.set_options(
        [
            # Client 1
            ("HiddenServiceDir", f"{PROJECT_PATH}/src/hidden_services/clients/client1"),
            ("HiddenServicePort", "5001 127.0.0.1:5001"),
            # Client 2
            ("HiddenServiceDir", f"{PROJECT_PATH}/src/hidden_services/clients/client2"),
            ("HiddenServicePort", "5025 127.0.0.1:5025"),
            # Server
            ("HiddenServiceDir", f"{PROJECT_PATH}/src/hidden_services/server"),
            ("HiddenServicePort", "5050 127.0.0.1:5050"),
        ]
    )
