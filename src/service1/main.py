from stem.control import Controller
from flask import Flask, Response, render_template, request
import requests
import os

HOST1, PORT1 = "127.0.0.1", 5000
hidden_svc1_dir = "c:/temp/service1"

HOST2, PORT2 = "127.0.0.1", 5001
hidden_svc2_dir = "c:/temp/service2"

PROXIES = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
}

session = requests.session()
session.proxies = PROXIES
app = Flask("P2P chat")

messages = []

@app.get("/")
def index():
    return render_template("template1.html")

@app.get("/inbox")
def root():
    return messages

@app.get("/receive")
def receive():
    msg = request.args.get("msg")
    # TODO: Maybe some validation?
    messages.append(msg)
    print(f"Received message: {msg}")
    print(messages)
    return Response(response="Received message", status="200")

@app.get("/send")
def send():
    address = request.args.get("address")
    msg = request.args.get("msg")

    res = session.get(f"http://{address}.onion/receive", params={"msg": msg})
    return Response(response="Sent", status=200) if res.status_code == 200 else Response(response="Error", status="500")

    
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