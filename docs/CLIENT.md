# P2P Tor Chat Client Documentation

This is a specification of the P2P Tor Chat client.

## Contents

- [Dependencies](#dependencies)
- [How it works?](#how-it-works)
- [Installation](#installation)
- [Server Connection](#server-connection)
- [Peer Connection](#peer-connection)
- [Message Encryption](#message-encryption)
- [Troubleshooting](#troubleshooting)

## Dependencies

- Tor Browser [Link to download](https://www.torproject.org/download/)
- Python 3.10 or higher
- [PySocks](https://pypi.org/project/PySocks/)
- [click](https://pypi.org/project/click/)
- [halo](https://pypi.org/project/halo/)
- [pycrypto](https://pypi.org/project/pycrypto/)


## How it works?

The client is a part of the P2P Tor Chat application. It is responsible for exchanging messages between peers. The client connects to the server to get information about other peers and then connects to them via Tor.

We use peer to peer to create decentralized message storage. Additionally, we use Tor so every peer stays anonymous.

## Installation

To install the client you need to follow the [general instructions](https://github.com/TomaszAgent/Peer2Peer-with-tor/blob/main/docs/INSTALL.md)

## Server Connection

When a client initiates a connection to the server via WebSocket, it undergoes a registration process. Initially, the client transmits its hidden service address and chosen unique nickname to the server for storage. Additionally, the client sends its public key to the server, facilitating encryption of messages by other peers or verification of the client's signature.

This process ensures that the server has the necessary information to facilitate secure communication between peers, while also allowing for identification and authentication within the network.

### Functions related to the server connection

- `client.py` `register()` - sending necessary information to the server
- `helpers.py` `get_users()` - getting information about other active peers from the server
- `client.py` `close_app()` - sending request to the server to remove the client from the list of active peers

## Peer Connection

After the client has registered with the server, it can connect to other peers. The client can send messages to other peers, and receive messages from them. The client can also create new chats with other peers.

The connection between peers starts with the client sending his public key, signature, and basic information (nick, hidden service address, port) to the peer. The peer can verify the signature and accepts or denies the connection.

After the connection is established, the client can send messages to the peer. The messages are encrypted with the peer's public key.

### Functions related to the peer connection
`client.py` `connect_to_user()` - sending connection request to the peer
`client.py` `new_connection()` - accepting or denying connection request from the peer
`client.py` `send_message()` - sending encrypted message to the peer
`client.py` `message_receiver()` - receiving and decrypting message from the peer
`client.py` `close_chat()` - closing the connection with the peer


## Message Encryption

The messages are encrypted with the peer's public key. The encryption is done with the RSA algorithm.

Additionally at the beginning of the connection, the client send his signature to the peer. The peer can verify the signature with the client's public key.

### Functions related to the message encryption
`security.py` - functions related to the security of the connection

## Troubleshooting

- `[WinError 10061] No connection could be made because the target machine actively refused it` - this error occurs when you try to run client without runnining Tor Browser. Make sure you have Tor Browser running before you start the client.

- `Received empty socket content` - this error occurs when `HiddenServiceDir` in the `config.ini` file is not set correctly. Make sure you have set the correct path to the hidden service directory.

- `Client: Socket error: 0x01: General SOCKS server failure` - this error occurs when `SERVER_ADDRESS` in the `config.ini` is not set or set incorrectly. Second reason for this error is when the server is not running. Make sure you have set the correct address of the server and that the server is running.

- `[Configuration error] Missing variables in config` - this error occurs when you have not set all the necessary variables in the `config.ini` file. Make sure you have set all the variables in the `config.ini` file.
