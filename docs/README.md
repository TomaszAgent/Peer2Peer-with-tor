# P2P Tor Chat

This is a peer to peer chat via Tor that allows user to communitaced while staying anonymous.

## Installation

See [general instructions]()
### Dependencies

- Tor Browser [Link to download](https://www.torproject.org/download/)
- Python 3.11.9 or higher

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
