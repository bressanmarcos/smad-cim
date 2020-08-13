if __name__ == "__main__":
    import socket

    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.connect(('localhost', 50000))
    
    # Envia dado
    socket.sendall(bytes('operate:CH13:open', "utf-8"))

    # Resposta
    response = str(socket.recv(1024), "utf-8")

    print(f'State: {response}')