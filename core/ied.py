import os
import socket
from pathlib import Path

from pade.misc.utility import call_in_thread, call_later, display_message

from core.common.enums import *


class IED():
    STATES = {'open': 1, 'close': 2, 'invalid': 0, 'intermediate': 3}
    REVERSE_STATES = {value: alias for alias, value in STATES.items()}
    VALID_STATES = ['open', 'close']

    def __init__(self, id, host, call_on_event=None):
        self.id = id
        self.ip = host[0]
        self.port = host[1]
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
    def __init__(self, id, host, filename, call_on_event=None, initial_breaker_position='close'):
        super().__init__(id, host, call_on_event)
        self.breaker_position = initial_breaker_position
        self.filename = Path(filename)

    def connect(self):
        """Conecta-se ao IED (stub)"""
        display_message(f'{self.id}@{self.ip}:{self.port}', 'Conectado')
        self.run()

    def operate(self, action):
        """Envia comando ao IED através de protocol específico"""
        if action not in IED.VALID_STATES:
            raise ValueError(f'Invalid action: {action}')
        # Envia dado
        self.breaker_position = action
        display_message(f'{self.id}@{self.ip}:{self.port}',
                        f'Comando {action} enviado')

    def get_breaker_position(self) -> str:
        """Retorna posição do breaker"""
        display_message(f'{self.id}@{self.ip}:{self.port}',
                        f'Posição atual: [{self.breaker_position}]')
        return self.breaker_position

    def handle_receive(self, *args):
        """Função automaticamente chamada quando
        mensagem do IED é recebida. Chama a função
        do agente de comunicação"""
        display_message(f'{self.id}@{self.ip}:{self.port}', f'Evento: {args}')
        # Assume que a presença de XCBR é para a abertura da chave
        if 'XCBR' in args and 'BRKF' not in args:
            self.breaker_position = 'open'

        call_in_thread(self.callback, self, *args)

    def run(self):
        """Lê arquivos com o mesmo nome da ID do switch
        a cada 5 segundos. Lê linha a linha e apaga.
        Os arquivos lidos se localizam em ``/core/ied/``"""

        def loop():
            try:
                # Abertura de arquivo
                with open(self.filename, 'r') as file:
                    # Lê primeira linha
                    data = file.readline().strip().split()
                    # Salva demais linhas
                    next_lines = file.readlines()

                # Reescreve demais linhas no mesmo arquivo
                with open(self.filename, 'w') as file:
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
    """Conecta-se a um IED simulado em outro IP:PORT"""

    def __init__(self, id, host, call_on_event=None):
        super().__init__(id, host, call_on_event)

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))
        # Atualiza a posição da chave
        self.get_breaker_position()
        display_message(f'{self.id}@{self.ip}:{self.port}', 'Conectado')
        self.run()

    def operate(self, action):
        """Envia comando ao IED através de protocol específico"""
        assert action in IED.VALID_STATES

        # Envia dado
        self.socket.sendall(bytes(f'operate:{action}', "utf-8"))

        # Resposta
        response = str(self.socket.recv(1024), "utf-8")

        # Salva posição enviada se ok
        if response == 'ok':
            # Obtém código do comando (IEC 61850)
            self.breaker_position = action

    def get_breaker_position(self) -> str:
        """Retorna posição do breaker"""
        # Envia dado
        self.socket.sendall(bytes('read', "utf-8"))

        # Resposta
        response = str(self.socket.recv(1024), "utf-8")

        if response not in IED.STATES:
            display_message(f'{self.id}@{self.ip}:{self.port}',
                            f'Unexpected return value: "{response}"')

        self.breaker_position = response
        return response

    def breaker_tripped(self) -> bool:
        """Verifica se breaker mudou de posição"""
        old_state = self.breaker_position
        new_state = self.get_breaker_position()

        return old_state == 'close' and new_state == 'open'

    def run(self):
        def loop():
            if self.breaker_tripped():
                display_message(f'{self.id}@{self.ip}:{self.port}',
                                'Abertura de chave detectada')
                args = ('XCBR',)
                call_in_thread(self.callback, self, *args)
            # Chama função novamente em 1 segundo
            call_later(1.0, loop)

        # Chama função pela primeira vez depois de 3 segundos
        call_later(3.0, loop)


if __name__ == "__main__":
    # Create a socket (SOCK_STREAM means a TCP socket)
    ied = SimulatedIED('CH13', ('localhost', 50013), print)
    ied.connect()
