# Installing P2P Tor Chat

- [Client Installation](#client-installation)

- [Server Installation](#server-installation)

- [Runing client and server on one machine](#run-client-and-server-on-one-machine)

## Client Installation

You can install the client from the last release. You can find the releases [here](https://github.com/TomaszAgent/Peer2Peer-with-tor/releases)

### Before you start

Before you start make sure you have installed all the dependencies that are listed in the [Client Documentation](https://github.com/TomaszAgent/Peer2Peer-with-tor/blob/main/docs/CLIENT.md)

### Configuration

To start chatting you need to configure the application. To do so you need to edit the `config.ini` file. You can find the file in the `client` directory.

The configuration file is divided into three sections: `Server`, `Host`, and `HiddenService`.

In the `Server` section you need to set up the address and the port of the server that will be used to store you and your peers' information. Example configuration:

```ini
[Server]
SERVER_ADDRESS = ghuew5eo6ug62rmhcd3wgdk3lnslklfotajjx2ugx67wmv5thscq6xyd.onion
SERVER_PORT = 5001
```

In the `Client` section you need to set up the address and the port of the client that will be used to exchange messages. We recommend not to change `HOST`. `PORT` is the port that the client will be listening on so make sure you choose free one. Example configuration:

```ini
[Host]
HOST = 127.0.0.1
PORT = 5050
```

In the `HiddenService` section you need to set up all your hidden services that you will use. You can add as many as you want. The format is as follows:

```ini
[HiddenService<service name>]
HiddenServiceDir = <path to the hidden service directory>
HiddenServicePort = <port> <address>:<port>
```

Example configuration:

```ini
[HiddenService1]
HiddenServiceDir = /home/user/hidden_service1
HiddenServicePort = 5050 localhost:5050
```

### Running the client

To run the client you simply need to open `client.exe` file.

If you encounter any problems please refer to the most common issues in the [Client Documentation](https://github.com/TomaszAgent/Peer2Peer-with-tor/blob/main/docs/CLIENT.md)

## Server Installation

You can install the server from the last release. You can find the releases [here](https://github.com/TomaszAgent/Peer2Peer-with-tor/releases)

### Before you start

Before you start make sure you have installed all the dependencies that are listed in the [Server Documentation](https://github.com/TomaszAgent/Peer2Peer-with-tor/blob/main/docs/SERVER.md)

### Configuration

To start the server you need to configure couple of things. To do so you need to edit the `config.ini` file. You can find the file in the `server` directory.

The configuration file is divided into three sections: `Host` and `HiddenService`.

In the `Host` section you need to set up the address and the port of the server that will be used to store you and your peers' information. We recommend not to change `HOST`. `PORT` is the port that the server will be listening on so make sure you choose free one. Example configuration:

```ini
[Host]
HOST = 127.0.0.1
PORT = 5050
```

In the `HiddenService` section you need to set up all your hidden services that you will use. You can add as many as you want. The format is as follows:

```ini
[HiddenService<service name>]
HiddenServiceDir = <path to the hidden service directory>
HiddenServicePort = <port> <address>:<port>
```

Example configuration:

```ini
[HiddenService1]
HiddenServiceDir = /home/user/hidden_service1
HiddenServicePort = 5050 localhost:5050
```

## Running the server

To run the client you simply need to open `server.exe` file.

If you encounter any problems please refer to the most common issues in the [Server Documentation](https://github.com/TomaszAgent/Peer2Peer-with-tor/blob/main/docs/SERVER.md)

## Runing client and server on one machine

If you want to run the client and the server on the same machine you need to set up the hidden services for the server and client in both `config.ini` in the `server` and `client` directories.

```ini
[HiddenServiceClient]
HiddenServiceDir = /path/to/client/hidden/service
HiddenServicePort = 5050 localhost:5050

[HiddenServiceServer]
HiddenServiceDir = /path/to/server/hidden/service
HiddenServicePort = 5001 localhost:5001
```

In `/path/to/server/hidden/service/hostname` you will find the address of the hidden service that you need to put in the `SERVER_ADDRESS` in the `config.ini` file of the client. Remember to change `SERVER_PORT` to the port that the server is listening on.

Then you need to run the server first and then the client. The client will connect to the server using the hidden service.
