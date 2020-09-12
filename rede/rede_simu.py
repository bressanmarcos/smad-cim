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

import imp, numpy as np

class Network():
    ESTADO_CODIGO = {'open': 0, 'close': 1}
    ESTADO_CODIGO_REVERSO = {value: key for key, value in ESTADO_CODIGO.items()}

    def __init__(self, filename, ip_filename):
        self.filename = filename
        self.io_lock = Lock()
        self.reset_network()
        self.ip_ied = imp.load_source('ip', ip_filename).ip_ied
        self.ip_ied_reverse_map = {value: key for key, value in self.ip_ied.items()}
        
        # Abre conexões com os sockets das chaves
        socket_chaves = []
        for nome in self.chaves:
            sock = socket.socket()
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(self.ip_ied[nome])
            sock.setblocking(0)
            sock.listen()
            socket_chaves.append(sock)

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
            if server in self.sockets_chaves:
                connection, client_address = server.accept()
                print(f'Connection from {client_address} to {server.getsockname()}')
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

                # Comando para IEDs
                switch = self.ip_ied_reverse_map[('localhost', port)]

                if command in ('read', 'operate'):
                    # Aciona comando se for Read ou Operate
                    next_msg = bytes(getattr(self, command)(switch, *message), 'utf-8')

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
        inputs = self.sockets_chaves[:]
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
            estado_atual = Network.ESTADO_CODIGO_REVERSO[self.chaves[switch].estado]

            def localizar_chave(chave):
                for se in self.subestacoes:
                    for alim in self.subestacoes[se].alimentadores.keys():
                        if chave in self.subestacoes[se].alimentadores[alim].chaves.keys():
                            return self.subestacoes[se].alimentadores[alim]

            def localizar_setor(setor):
                for se in self.subestacoes:
                    for alim in self.subestacoes[se].alimentadores.keys():
                        if setor in self.subestacoes[se].alimentadores[alim].setores.keys():
                            return self.subestacoes[se].alimentadores[alim]  
            
            if estado_atual == 'close' and action == 'open':
                # Busca o setor vizinho à chave que será podado
                # alim = localizar_chave(switch)
                # valor_mais_profundo = -1
                # setor_mais_profundo = None
                # for n in ('n1', 'n2'):
                #     setor = getattr(self.chaves[switch], n).nome
                #     prof = np.where(alim.rnp[1, :] == setor)[0][0]
                #     if prof > valor_mais_profundo:
                #         valor_mais_profundo = prof
                #         setor_mais_profundo = setor

                # Muda estado da chave
                self.chaves[switch].estado = Network.ESTADO_CODIGO[action]

                # Salva a poda
                # poda = alim.podar(setor_mais_profundo, alterar_rnp=True)
                # self.podas.append(poda)

            
            elif estado_atual == 'open' and action == 'close':
                # Busca a poda salva que contém o switch recém aberto
                # poda_buscada = None
                # for poda in self.podas:
                #     if switch in poda[6]:
                #         poda_buscada = poda

                # # Recupera a poda salva
                # try:
                #     poda = self.podas.pop(poda_buscada)
                # except KeyError:
                #     print('Short-circuit between feeders!')

                # # Busca o setor vizinho à chave, que alimentará a poda
                # setor_colab = None
                # for n in ('n1', 'n2'):
                #     setor = getattr(poda[6], n).nome
                #     if setor not in poda[0]:
                #         setor_colab = setor
                #         n_ = next(n_ for n_ in ('n1', 'n2') if n != n_)
                #         setor_raiz = getattr(poda[6], n_).nome
                # alim = localizar_setor(setor_colab)

                # Muda estado da chave
                self.chaves[switch].estado = Network.ESTADO_CODIGO[action]

                # Insere poda ao novo alimentador
                # alim.inserir_ramo(setor_colab, poda, setor_raiz)


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
    Network(os.path.dirname(__file__) + '/models/new-network.xml', '').run()