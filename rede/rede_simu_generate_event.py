import socket

def send(message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 50000))
    # Envia dado
    sock.sendall(bytes(message, "utf-8"))
    # Resposta
    response = str(sock.recv(1024), "utf-8")
    print(f'State: {response}')

if __name__ == "__main__":
    # send('operate:CH18:close')
    send('operate:CH18:open')
    # send('reset')
