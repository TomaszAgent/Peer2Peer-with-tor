# Peer to Peer Chat Application

This is a peer to peer chat via Tor that allows user to communitaced while staying anonymous.

## Installation

From realease page download the latest version of the application

### Dependencies

- Tor Browser [Link to download](https://www.torproject.org/download/)
- Python 3.8 or higher

### Configuration

You can configure the application by editing the `_config.py` file.

In the `_config.py` file you can set the following options:
-SERVER ADDRESS - the address of the server that will be used to connect to the network (e.g. `yhpc3gkjqemsfpc4hcnfrvciil3xqgis4ipqfgootcgigawltlunxzqd.onion`). By default there is no server address set.
- SERVER PORT - server port. By default it is set to `5001`. Change it if server uses different port.
- HOST - host address. By default it is set to `127.0.0.1`. Do not change it unless you know what you are doing.
- PORT - port. By default it is set to `5050`. Change it if you want to use different port.

### Running

To run the application you need to have Tor Browser running in the background. Then you can simply run the executable file that you downloaded from the release page.

## Authors

- [nokokiii](www.github.com/nokokiii)
- [TomaszAgent](www.github.com/TomaszAgent)
