from threading import Lock
import socket
import select
import queue
import os
os.sys.path.insert(0, os.getcwd())

import json
from pathlib import Path
from pprint import pprint 

from rede.rdf2mygrid import carregar_topologia
from mygrid.fluxo_de_carga.varred_dir_inv import calcular_fluxo_de_carga

class Network():

    def __init__(self, filename):
        self.filename = filename
        self.io_lock = Lock()
        self.reset_network()
        
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
 
    def reset_network(self):
        # Carregar topologia
        self.subestacoes = carregar_topologia(Path(self.filename))
        self.podas = []

        # Chaves e instâncias
        self.chaves = {key: value for subs in self.subestacoes.values() for alim in subs.alimentadores.values() for key, value in alim.chaves.items()}
        # Trechos
        self.trechos = {key: value for subs in self.subestacoes.values() for alim in subs.alimentadores.values() for key, value in alim.trechos.items()}
        # Nós
        self.nos = {key: value for subs in self.subestacoes.values() for alim in subs.alimentadores.values() for key, value in alim.nos_de_carga.items()}

    def io(self, inputs, outputs, message_queues):
        readable, writable, exceptional = select.select(inputs, outputs, inputs, 0.2)

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
                    # Reseta estado da rede
                    self.reset_network()
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

    def calculate_flow(self):
        def verificar_correntes(self, subestacao):

            for alimentador in subestacao.alimentadores.values():
                for trecho in alimentador.trechos.values():

                    if trecho.fluxo.mod > trecho.condutor.ampacidade:
                        print(f'Restrição de carregamento de condutores ({round(trecho.fluxo.mod, 2)} A > {trecho.condutor.ampacidade} A) atingida no trecho {trecho.nome}')
                        return trecho.nome
            else:
                return None
        def verificar_tensoes(self, subestacao):

            for alimentador in subestacao.alimentadores.values():
                    for no in alimentador.nos_de_carga.values():
                        if no.tensao.mod < 0.8 * subestacao.tensao.mod or \
                            no.tensao.mod > 1.05 * subestacao.tensao.mod:
                            print(f'Restrição de Tensão atingida no nó de carga {no.nome}')
                            print(f'{round(no.tensao.mod, 2)} V fora do intervalo [{0.8 * subestacao.tensao.mod} V, {1.05 * subestacao.tensao.mod} V]')
                            return no.nome, round(no.tensao.mod/subestacao.tensao.mod,4)
            else:
                return None

        for SED in self.subestacoes.values():
            with self.io_lock:
                calcular_fluxo_de_carga(SED)
        
    def switch_reaction(self):
        pass

    def run(self):
        inputs = [self.socket_evento] + self.sockets_chaves
        outputs = []
        message_queues = {}
        
        while inputs:
            self.calculate_flow()
            self.switch_reaction()
            self.io(inputs, outputs, message_queues)

    # Switches
    def operate(self, switch, action):
        """Change the state of a switch remotely"""
        self.write(switch, action)
        return 'ok'

    def write(self, switch, action):
        with self.io_lock:
            estados = {'open': 0, 'close': 1}
            self.chaves[switch].estado = estados[action]

            # if action == 'open':
            #     def localizar_setor(self, setor = str):
            #         for se in self.topologia_subestacao:
            #             for alim in self.topologia_subestacao[se].alimentadores.keys():
            #                 if setor in self.topologia_subestacao[se].alimentadores[alim].setores.keys():
            #                     return self.topologia_subestacao[se].alimentadores[alim]

            #     setor_nome = self.chaves[switch].n2.nome
            #     alim = localizar_setor(setor_nome)
            #     self.podas.append(alim.podar(setor_nome, alterar_rnp=True))
            
            # elif action == 'close':
            #     poda = self.podas.pop()
            #     for n in ('n1', 'n2'):
            #         pass

    def read(self, switch):
        """Read the current state of a switch remotely"""
        with self.io_lock:
            estados = {0: 'open', 1: 'close'}
            state = estados[self.chaves[switch].estado]
            return state

    # Trechos
    def read_segments_load(self, trecho):
        with self.io_lock:
            return self.trechos[trecho].fluxo

    # Nós de carga
    def read_energy_consumers_voltage(self, no):
        with self.io_lock:
            return self.nos[no].tensao

if __name__ == "__main__":
    Network(os.path.dirname(__file__) + '/models/rede-cim.xml').run()