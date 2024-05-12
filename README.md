# Peer to Peer Chat Application

This is a peer to peer chat via Tor that allows user to communitaced while staying anonymous.

## Installation

From realease page download the latest version of the application

### Dependencies

- Tor Browser [Link to download](https://www.torproject.org/download/)
- Python 3.11.9 or higher

### Configuration

You can configure the application by editing the `config.ini` file.

In the `config.ini` file you can set the following options

Server configuration:
- `SERVER_ADDRESS` - the address of the server that will be used to exchange messages (e.g. `ghuew5eo6ug62rmhcd3wgdk3lnslklfotajjx2ugx67wmv5thscq6xyd.onion`)
- `SERVER_PORT` - the port of the server that will be used to exchange messages (e.g. `5001`)

Client configuration:
- `HOST` - the address of the client that will be used to exchange messages (e.g. `127.0.0.1`). Change it only if you what you're doing.
- `PORT` - the port of the client that will be used to exchange messages (e.g. `5050`)

Tor configuration:

Here you need to set up all your hidden services that you will use. You can add as many as you want. The format is as follows:

```
[HiddenService<service name>]
HiddenServiceDir = <path to the hidden service directory>
HiddenServicePort = <port> <address>:<port>
```

Name in the `[]` must start with `HiddenService`. The `HiddenServiceDir` is the path to the directory where the hidden service will be stored. The `HiddenServicePort` is the port that the hidden service will be listening on and the address and port that the hidden service will be forwarding to. In most cases address is `localhost` and port is free port that you service can work on.

Example configuration:

```
[HiddenService1]
HiddenServiceDir = /home/user/hidden_service1
HiddenServicePort = 5001 localhost:5001
```

## Running

To run the application you need to have Tor Browser running in the background. Then you can simply run the executable file that you downloaded from the release page.

### Run client and serve on one machine

If you want to run the client and the server on the same machine you need to set up the hidden service for the server. You can do this by adding the following configuration to the `config.ini` file in both the client and the server:

```
[HiddenServiceClient]
HiddenServiceDir = /path/to/client/hidden/service
HiddenServicePort = 5050 localhost:5050

[HiddenServiceServer]
HiddenServiceDir = /path/to/server/hidden/service
HiddenServicePort = 5001 localhost:5001
```

In `/path/to/server/hidden/service/hostname` you will find the address of the hidden service that you need to put in the `SERVER_ADDRESS` in the `config.ini` file of the client. Remember to change `SERVER_PORT` to the port that the server is listening on.

Then you need to run the server first and then the client. The client will connect to the server using the hidden service.

## Troubleshooting

TODO - add most common problems and solutions

## Authors

- [nokokiii](www.github.com/nokokiii)
- [TomaszAgent](www.github.com/TomaszAgent)
