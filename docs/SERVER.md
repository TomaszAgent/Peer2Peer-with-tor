# P2P Tor Chat Server Documentation

This is a specification of the P2P Tor Chat server.

## Contents

- [Dependencies](#dependencies)
- [How it works?](#how-it-works)
- [Installation](#installation)
- [Peer Connection](#peer-connection)
- [Troubleshooting](#troubleshooting)

## Dependencies

- Tor Browser [Link to download](https://www.torproject.org/download/)
- [Python 3.10](https://www.python.org/downloads/) or higher
- [PySocks](https://pypi.org/project/PySocks/)
- [click](https://pypi.org/project/click/)
- [halo](https://pypi.org/project/halo/)
- [pycrypto](https://pypi.org/project/pycrypto/)


## How it works?

The server is a part of the P2P Tor Chat application. It is responsible for storing information about peers and facilitating communication between them. It's making easier to find neccecary information about other peers.

## Installation

To install the server you need to follow the [general instructions](https://github.com/TomaszAgent/Peer2Peer-with-tor/blob/main/docs/INSTALL.md)

## Peer Connection

When a peer establishes a connection to the server via WebSocket, it initiates a registration process to facilitate secure communication within the network. This process involves the peer transmitting essential information to the server for storage and authentication purposes.

1. Hidden Service Address and Unique Nickname: Upon connection establishment, the peer sends its hidden service address along with a chosen unique nickname to the server. This information is stored by the server to facilitate identification of the peer within the network.

2. Public Key Transmission: In addition to the address and nickname, the peer also sends its public key to the server. This key serves multiple purposes:
    - Encryption: Other peers can utilize this public key to encrypt messages intended for the peer, ensuring secure communication.
    - Signature Verification: The server can use the public key to verify the authenticity of messages signed by the peer, enhancing network security.

By collecting and storing this information during the registration process, the server ensures that it possesses the necessary data to enable secure and authenticated communication between peers within the network.

### Functions related to the peer connection

[`server.py`](https://github.com/TomaszAgent/Peer2Peer-with-tor/blob/main/server/server.py):
- `connection_handler()` - handling incoming connections from peers
- `register_user()` - registering a new peer to list of active peers
- `handle_request()` - handling requests from peers

## Troubleshooting

- `[WinError 10061] No connection could be made because the target machine actively refused it` - this error occurs when you try to run server without runnining Tor Browser. Make sure you have Tor Browser running before you start the server.

- `Received empty socket content` - this error occurs when `HiddenServiceDir` in the `config.ini` file is not set correctly. Make sure you have set the correct path to the hidden service directory.

- `[Configuration error] Missing variables in config` - this error occurs when you have not set all the necessary variables in the `config.ini` file. Make sure you have set all the variables in the `config.ini` file.
