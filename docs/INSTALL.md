# Installing P2P Tor Chat

- [Client Installation](#client-installation)

- [Server Installation](#server-installation)

## Client Installation


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


## Server Installation