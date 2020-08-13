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
        
        self.chaves = {nome: (obj, socket.socket()) for nome, obj in chaves.items()}

        for nome, data in self.chaves.items():
            _, sock = data
            port = 50000 + int(nome.split('CH')[1])
            sock.bind(('localhost', port))
            sock.listen()
            sock.setblocking(0)

        self.sockets = [data[1] for data in self.chaves.values()]
 
    def run(self):
        select_inputs = self.sockets[:]
        select_outputs = []
        message_queues = {}
        
        while select_inputs:
            readable, writable, exceptional = select.select(select_inputs, select_outputs, select_inputs)

            for server in readable:
                if server in self.sockets:
                    connection, client_address = server.accept()
                    connection.setblocking(0)
                    select_inputs.append(connection)
                    message_queues[connection] = queue.Queue()
                else:
                    data = server.recv(1024)
                    if data:
                        message_queues[server].put(data)
                        if server not in select_outputs:
                            select_outputs.append(server)
                    else:
                        if server in select_outputs:
                            select_outputs.remove(server)
                        select_inputs.remove(server)
                        server.close()
                        del message_queues[server]
            
            for server in writable:
                try:
                    message = str(message_queues[server].get_nowait().strip(), 'utf-8')
                    message = message.split(':')

                    port = server.getsockname()[1]
                    switch = 'CH' + str(port - 50000)

                    command = message.pop(0)
                    next_msg = getattr(self, command)(switch, *message)
                except queue.Empty:
                    select_outputs.remove(server)
                else:
                    server.send(next_msg)

            for server in exceptional:
                select_inputs.remove(server)
                if server in select_outputs:
                    select_outputs.remove(server)
                server.close()
                del message_queues[server]

    def operate(self, switch, action):
        estados = {'open': 0, 'close': 1}
        self.chaves[switch][0].estado = estados[action]
        return b'ok'

    def read(self, switch):
        estados = {0: 'open', 1: 'close'}
        return bytes(estados[self.chaves[switch][0].estado], 'utf-8')

if __name__ == "__main__":
    Network().run()