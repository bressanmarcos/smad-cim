import os
os.sys.path.insert(0, os.getcwd()) 
# Adiciona ao Path a pasta raiz do projeto

import pytest
import multiprocessing
import subprocess
import time
from random import randint

from pade.core import new_ams
from pade.core.sniffer import Sniffer
from pade.misc.utility import start_loop as st_loop
from pade.core.agent import Agent_

from core.common import to_elementtree, to_string, dump # pylint: disable=import-error,no-name-in-module

def start_loop(agents, seconds=20.0):
    """Encapsula o start_loop de modo que quando chamado
    ele seja executado em outro processo por 20 segundos. \\
    Ideal para ser usado em testes"""

    p = multiprocessing.Process(target=st_loop, args=(agents,))
    p.start(), time.sleep(seconds), p.kill()


@pytest.fixture(scope='function')
def run_ams():
    """Inicializa o AMS do PADE e retorna a instância do ``sniffer``.
    Essa instância pode ser usada para incluir ou não o ``sniffer``
    dentro do ``start_loop`` e para capturar o endereço do AMS no
    atributo ``sniffer.ams`` para ser definida por outros agentes.
    Este artifício permite testar diversas instâncias do PADE ao
    mesmo tempo, já que cada AMS é executado numa porta distinta."""

    # Define IP e porta do AMS
    ams_dict = {'name': 'localhost', 'port': randint(10000, 60000)}

    # Executa AMS num subprocesso com ``python new_ams.py user email pass {porta}``
    commands = ['python', new_ams.__file__, 'pade_user', 'email@', '12345', str(ams_dict['port'])]
    p = subprocess.Popen(commands, stdin=subprocess.PIPE)

    # Instancia Sniffer para ser executado na {porta+1}
    sniffer = Sniffer(host=ams_dict['name'], port=ams_dict['port']+1)
    sniffer.ams = ams_dict

    # Dá pequeno delay antes de iniciar teste
    time.sleep(2.0)

    # Inicia teste
    yield sniffer

    # Finaliza AMS após execução de teste
    print('\nKilling AMS')
    p.kill()

@pytest.fixture(scope='function')
def deactivate_send_message(monkeypatch):
    """Evita o envio de mensagem por todos os agentes, 
    Em vez disso, imprime na tela a mensagem que seria enviada
    """
    monkeypatch.setattr(Agent_, "_send", lambda self, message, receivers: dump(message))

@pytest.fixture(scope='function')
def debug_send_message(monkeypatch):
    """Printa na tela todas as mensagens enviadas pelos agentes
    (inclusive sniffer e ams)."""
    def stack_send(original_send):
        def wrap_send(self, message, receivers):
            dump(message)
            return original_send(self, message, receivers)
        return wrap_send
    monkeypatch.setattr(Agent_, '_send', stack_send(Agent_._send))

@pytest.fixture(scope='function')
def deactivate_call_later(monkeypatch):
    """Impede o uso de call_later"""
    monkeypatch.setattr(Agent_, "call_later", lambda self, time, method, *args: 1)



