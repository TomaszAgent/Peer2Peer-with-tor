from stem.control import Controller
from flask import Flask, request, Response
import os

app = Flask("P2P chat")
HOST1, PORT1 = "127.0.0.1", 5000
hidden_svc1_dir = "c:/Peer2Peer-with-tor/service1"

HOST2, PORT2 = "127.0.0.1", 5001
hidden_svc2_dir = "c:/Peer2Peer-with-tor/service2"

messages = []

@app.get('/')
def index():
    return messages

@app.get("/inbox")
def inbox():
    msg = request.args.get("msg")
    messages.append(msg)
    return Response(response="Received message", status="200")
    
if __name__ == "__main__":
    print(" * Getting controller")
    controller = Controller.from_port(address="127.0.0.1", port=9151)
    try:
        controller.authenticate()
        controller.set_options(
          [
            ("HiddenServiceDir", hidden_svc1_dir),
            ("HiddenServicePort", f"80 {HOST1}:{str(PORT1)}"),
            ("HiddenServiceDir", hidden_svc2_dir),
            ("HiddenServicePort", f"81 {HOST2}:{str(PORT2)}"),
          ]
        )
        svc_name = open(f"{hidden_svc1_dir}/hostname", "r").read().strip()
        print(f" * Created host: {svc_name}")
    except Exception as e:
        print(" * Error creating host")
        print(e)
    app.run(port=PORT1)