def read_data(c):
    data = b''
    while b'\n' not in data:
        data += c.recv(1)

    return data.decode()
