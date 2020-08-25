import socket

def send(message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 50000))
    # Envia dado
    sock.sendall(bytes(message, "utf-8"))
    # Resposta
    response = str(sock.recv(1024), "utf-8")
    print(f'Status: {response}')
    sock.close()

def read_all():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 50000))
    for i in range(1,20):
        # Envia dado
        sock.sendall(bytes(f'read:CH{i}', "utf-8"))
        # Resposta
        response = str(sock.recv(1024), "utf-8")
        print(f'CH{i}: {response}')
    sock.close()

if __name__ == "__main__":
    # send('operate:CH18:close')
    send('operate:CH1:open')
    # send('operate:CH1:open')
    # read_all()
