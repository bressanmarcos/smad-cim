import os
os.sys.path.insert(0, os.getcwd()) 
# Adiciona ao Path a pasta raiz do projeto

from pathlib import Path
from pade.misc.utility import display_message, call_in_thread, call_later

class IED():
    STATES = {'open': 1, 'close': 2, 'invalid': 0, 'intermediate': 3}
    REVERSE_STATES = {value: alias for alias, value in STATES.items()}
    VALID_STATES = ['open', 'close']


    def __init__(self, _id, ip, call_on_event, initial_breaker_position='close'):
        self.id = _id
        self.ip = ip
        self.breaker_position = IED.STATES[initial_breaker_position]
        self.callback = call_on_event


    def connect(self):
        """Conecta-se ao IED (stub)"""
        display_message(f'{self.id}@{self.ip}', 'Conectado')
        self.run()
        # TODO: Inicializar atributos da classe IED com dados do IED


    def operate(self, action):
        """Envia comando ao IED através de protocol específico"""
        if action not in IED.VALID_STATES:
            raise ValueError(f'Invalid action: {action}') 
        # Obtém código do comando (IEC 61850)
        value_to_write = IED.STATES[action]
        # Envia dado
        if self.breaker_position == value_to_write:
            display_message(f'{self.id}@{self.ip}', 'Chave já está na posição solicitada')
        else:
            self.breaker_position = value_to_write
            display_message(f'{self.id}@{self.ip}', f'Comando {value_to_write} ({action}) enviado')
      

    def get_breaker_position(self):
        """Retorna posição do breaker"""
        display_message(f'{self.id}@{self.ip}', \
            f'Posição: {self.breaker_position} ({IED.REVERSE_STATES[self.breaker_position]})')
        return IED.STATES[self.breaker_position] 


    def handle_receive(self, *args):
        """Função automaticamente chamada quando
        mensagem do IED é recebida. Chama a função
        do agente de comunicação"""
        display_message(f'{self.id}@{self.ip}', f'Evento: {args}')
        # Assume que a presença de XCBR é para a abertura da chave
        if 'XCBR' in args and 'BRKF' not in args:
            self.breaker_position = IED.STATES['open']
        call_in_thread(self.callback, self, *args)
        # self.callback(self, *args)
    

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
            call_later(7.0, loop)

        # Chama função pela primeira vez depois de 3 segundos
        call_later(9.0, loop)