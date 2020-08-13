import socket
import os
os.sys.path.insert(0, os.getcwd()) 
# Adiciona ao Path a pasta raiz do projeto

from pathlib import Path
from pade.misc.utility import display_message, call_in_thread, call_later

class SwitchAlreadyInPosition(Exception):
    pass

class IED():
    STATES = {'open': 1, 'close': 2, 'invalid': 0, 'intermediate': 3}
    REVERSE_STATES = {value: alias for alias, value in STATES.items()}
    VALID_STATES = ['open', 'close']


    def __init__(self, id, ip, port, call_on_event):
        self.id = id
        self.ip = ip
        self.port = port
        self.callback = call_on_event

    def connect(self):
        """Conecta-se ao IED"""
        raise NotImplementedError()

    def operate(self, action):
        """Envia comando ao IED através de protocol específico"""
        raise NotImplementedError()
 
    def get_breaker_position(self) -> str:
        """Retorna posição do breaker"""
        raise NotImplementedError()

class FileIED(IED):
    def __init__(self, id, ip, port, call_on_event, initial_breaker_position='close'):
        super().__init__(id, ip, port, call_on_event)
        self.breaker_position = IED.STATES[initial_breaker_position]

    def connect(self):
        """Conecta-se ao IED (stub)"""
        display_message(f'{self.id}@{self.ip}:{self.port}', 'Conectado')
        self.run()
        # TODO: Inicializar atributos da classe IED com dados do IED

    def operate(self, action):
        """Envia comando ao IED através de protocol específico"""
        if action not in IED.VALID_STATES:
            raise ValueError(f'Invalid action: {action}') 
        # Obtém código do comando (IEC 61850)
        value_to_write = IED.STATES[action]
        # Envia dado
        self.breaker_position = value_to_write
        display_message(f'{self.id}@{self.ip}:{self.port}', f'Comando {value_to_write} ({action}) enviado')

    def get_breaker_position(self) -> str:
        """Retorna posição do breaker"""
        display_message(f'{self.id}@{self.ip}:{self.port}', \
            f'Posição atual: {self.breaker_position} ({IED.REVERSE_STATES[self.breaker_position]})')
        return IED.REVERSE_STATES[self.breaker_position] 

    def handle_receive(self, *args):
        """Função automaticamente chamada quando
        mensagem do IED é recebida. Chama a função
        do agente de comunicação"""
        display_message(f'{self.id}@{self.ip}:{self.port}', f'Evento: {args}')
        # Assume que a presença de XCBR é para a abertura da chave
        if 'XCBR' in args and 'BRKF' not in args:
            self.breaker_position = IED.STATES['open']
        call_in_thread(self.callback, self, *args)

    def run(self):
        """Lê arquivos com o mesmo nome da ID do switch
        a cada 5 segundos. Lê linha a linha e apaga.
        Os arquivos lidos se localizam em ``/core/ied/``"""
        filename = Path(f'./core/ied/{self.id}.txt')

        def loop():
            try:
                # Abertura de arquivo
                with open(filename, 'r') as file:
                    # Lê primeira linha
                    data = file.readline().strip().split()
                    # Salva demais linhas
                    next_lines = file.readlines()
                
                # Reescreve demais linhas no mesmo arquivo
                with open(filename, 'w') as file:
                    # Reescreve demais linhas
                    for line in next_lines:
                        file.write(line)

                if data and data[0] != '':
                    # Envia para função que manipula recepção de valor
                    self.handle_receive(*data)

            except FileNotFoundError:
                # Caso o arquivo não exista
                pass

            # Chama função novamente em 1 segundo
            call_later(1.0, loop)

        # Chama função pela primeira vez depois de 3 segundos
        call_later(3.0, loop)

class SimulatedIED(IED):
    def __init__(self, id, ip, port, call_on_event):
        super().__init__(id, ip, port, call_on_event)
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.socket.connect((self.ip, self.port))
        
    def operate(self, action):
        """Envia comando ao IED através de protocol específico"""
        assert action in IED.VALID_STATES
        
        # Envia dado
        self.socket.sendall(bytes(f'operate:{action}', "utf-8"))
        display_message(f'{self.id}@{self.ip}:{self.port}', f'Comando {action} enviado')
        
        # Resposta
        response = str(self.socket.recv(1024), "utf-8")
        display_message(f'{self.id}@{self.ip}:{self.port}', f'Recebido {response}')
        
        # Salva posição enviada se ok
        if response == 'ok':
            # Obtém código do comando (IEC 61850)
            value_to_write = IED.STATES[action]
            self.breaker_position = value_to_write

    def get_breaker_position(self) -> str:
        """Retorna posição do breaker"""
        # Envia dado
        self.socket.sendall(bytes('read', "utf-8"))

        # Resposta
        response = str(self.socket.recv(1024), "utf-8")
        display_message(f'{self.id}@{self.ip}:{self.port}', f'Posição atual: {response}')
        self.breaker_position = IED.STATES[response]

        return response

if __name__ == "__main__":
    # Create a socket (SOCK_STREAM means a TCP socket)
    ied = SimulatedIED('CH13', 'localhost', 50013, print)
    ied.connect()
    pos = ied.get_breaker_position()

    print(f'Posição é a seguinte: {pos}')

    ied.operate('close')
    ied.operate('open')