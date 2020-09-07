import socket
import select
import queue
import os
os.sys.path.insert(0, os.getcwd())

import json
from pathlib import Path
from pprint import pprint 

from rede.rdf2mygrid import carregar_topologia

class Network():

    def __init__(self):
        self.reset_switches()
        
        # Abre conexões com os sockets das chaves
        socket_chaves = []
        for nome, _ in self.chaves.items():
            port = 50000 + int(nome.split('CH')[1])
            sock = socket.socket()
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
 
    def reset_switches(self):
        # Carregar topologia
        self.subestacoes = carregar_topologia(Path(os.path.dirname(__file__) + '/rede-cim-3.xml'))
        
        # Chaves e instâncias
        self.chaves = {key: value for subs in self.subestacoes.values() for alim in subs.alimentadores.values() for key, value in alim.chaves.items()}

    def io(self, inputs, outputs, message_queues):
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

                    if port == 50000:
                        # Simulação de eventos
                        switch = message.pop(0)
                    elif port > 50000:
                        # Comando para IEDs
                        switch = f'CH{port-50000}'

                    if command in ('read', 'operate'):
                        # Aciona comando se for Read ou Operate
                        next_msg = bytes(getattr(self, command)(switch, *message), 'utf-8')
                    
                    elif command == 'reset' and port == 50000:
                        # Reseta estados dos switches
                        self.reset_switches()
                        next_msg = b'ok'

                except queue.Empty:
                    outputs.remove(server)
                except:
                    next_msg = b'erro'
                    server.send(next_msg)
                else:
                    server.send(next_msg)

            for server in exceptional:
                inputs.remove(server)
                if server in outputs:
                    outputs.remove(server)
                server.close()
                del message_queues[server]

    def run(self):
        inputs = [self.socket_evento] + self.sockets_chaves
        outputs = []
        message_queues = {}
        
        while inputs:
            self.io(inputs, outputs, message_queues)

    def operate(self, switch, action):
        """Change the state of a switch remotely"""
        estados = {'open': 0, 'close': 1}
        self.chaves[switch].estado = estados[action]
        return 'ok'

    def read(self, switch):
        """Read the current state of a switch remotely"""
        estados = {0: 'open', 1: 'close'}
        state = estados[self.chaves[switch].estado]
        return state


if __name__ == "__main__":
    Network().run()