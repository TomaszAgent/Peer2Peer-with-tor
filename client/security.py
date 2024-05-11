import base64
import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


def encrypt(message: str, public_key: rsa.RSAPublicKey) -> bytes:
    """
    Encrypts a message using the provided RSA public key.
    """
    return public_key.encrypt(message.encode(), padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))


def decrypt(message: bytes, private_key: rsa.RSAPrivateKey) -> str:
    """
    Decrypts an encrypted message using the provided RSA private key.
    """
    return private_key.decrypt(message, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)).decode()


def rsa_keypair() -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    """
    Generates a RSA key pair consisting of a private key and its corresponding public key.
    """
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    return (private_key, private_key.public_key())


def sign(message: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
    """
    Signs a message using the provided RSA private key, generating a signature.
    """
    padding_instance = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)
    return base64.b64encode(private_key.sign(message, padding_instance, hashes.SHA256()))


def verify(message: bytes, signature: str, public_key: rsa.RSAPublicKey) -> bool:
    """
    Verifies the authenticity of a message by verifying its signature using the provided RSA public key.
    """
    sig = base64.b64decode(signature)
    padding_instance = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)
    try:
        public_key.verify(sig, message, padding_instance, hashes.SHA256())
        return True
    except cryptography.exceptions.InvalidSignature:
        return False
