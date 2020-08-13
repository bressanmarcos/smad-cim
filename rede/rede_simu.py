import socket
import select
import os
import queue
os.sys.path.insert(0, os.getcwd())

import json
from pathlib import Path
from pprint import pprint 

from rdf2mygrid import carregar_topologia

class Network():

    def __init__(self):
        # Carregar topologia
        self.subestacoes = carregar_topologia(Path(os.path.dirname(__file__) + '/rede-cim-3.xml'))
        chaves = {key: value for subs in self.subestacoes.values() for alim in subs.alimentadores.values() for key, value in alim.chaves.items()}
        
        # Chaves e instâncias
        self.chaves = chaves
        
        # Abre conexões com os sockets das chaves
        socket_chaves = []
        for nome, data in chaves.items():
            port = 50000 + int(nome.split('CH')[1])
            sock = socket.socket()
            sock.bind(('localhost', port))
            sock.listen()
            sock.setblocking(0)
            socket_chaves.append(sock)

        # Abre um socket para manipular eventos
        socket_evento = socket.socket()
        socket_evento.bind(('localhost', 50000))
        socket_evento.listen()
        socket_evento.setblocking(0)

        self.socket_evento = socket_evento
        self.sockets_chaves = socket_chaves
 
    def run(self):
        inputs = [self.socket_evento] + self.sockets_chaves
        outputs = []
        message_queues = {}
        
        while inputs:
            readable, writable, exceptional = select.select(inputs, outputs, inputs)

            for server in readable:
                if server in self.sockets_chaves or server is self.socket_evento:
                    connection, client_address = server.accept()
                    print(f'Connection from {client_address}')
                    connection.setblocking(0)
                    inputs.append(connection)
                    message_queues[connection] = queue.Queue()
                else:
                    data = server.recv(1024)
                    if data:
                        message_queues[server].put(data)
                        if server not in outputs:
                            outputs.append(server)
                    else:
                        if server in outputs:
                            outputs.remove(server)
                        inputs.remove(server)
                        server.close()
                        del message_queues[server]
            
            for server in writable:
                try:
                    port = server.getsockname()[1]

                    message = str(message_queues[server].get_nowait().strip(), 'utf-8').split(':')
                    command = message.pop(0)

                    # Simulação de eventos
                    if port == 50000:
                        switch = message.pop(0)
                    # Comando para IEDs
                    elif port > 50000:
                        switch = f'CH{port-50000}'

                    if command in ('read', 'operate'):
                        next_msg = getattr(self, command)(switch, *message)
                    else:
                        next_msg = b'erro'

                except queue.Empty:
                    outputs.remove(server)
                except:
                    pass
                else:
                    server.send(next_msg)

            for server in exceptional:
                inputs.remove(server)
                if server in outputs:
                    outputs.remove(server)
                server.close()
                del message_queues[server]

    def operate(self, switch, action):
        """Change the state of a switch remotely"""
        print(f'Operate, {switch}, {action}')
        estados = {'open': 0, 'close': 1}
        self.chaves[switch].estado = estados[action]
        return b'ok'

    def read(self, switch):
        """Read the current state of a switch remotely"""
        estados = {0: 'open', 1: 'close'}
        state = bytes(estados[self.chaves[switch].estado], 'utf-8')
        print(f'Read, {switch}')
        return state


if __name__ == "__main__":
    Network().run()