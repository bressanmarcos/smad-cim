import multiprocessing
import os
import subprocess
import time
from random import randint

import pytest
from core.common import dump, to_elementtree, to_string
from pade.core import new_ams
from pade.core.agent import Agent_
from pade.core.sniffer import Sniffer

from pade.plus.testing import start_loop_test
from pade.plus.testing import start_runtime


@pytest.fixture(scope='module')
def simular_IEDs():
    """Executa o simulador para IEDs em outra thread"""
    # Instancia classe
    network = Network('', '')

    # Executa loop em novo processo
    p = multiprocessing.Process(target=network.run)
    p.start()

    # Inicializa testes
    yield

    # Finaliza execução dos IEDs
    print('\nKilling IEDs')
    p.kill()


@pytest.fixture(scope='function')
def deactivate_send_message(monkeypatch):
    """Evita o envio de mensagem por todos os agentes, 
    Em vez disso, imprime na tela a mensagem que seria enviada
    """
    monkeypatch.setattr(Agent_, "_send", lambda self,
                        message, receivers: dump(message))


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
    monkeypatch.setattr(Agent_, "call_later", lambda self,
                        time, method, *args: 1)


@pytest.fixture(scope='session')
def queue():
    q = multiprocessing.Queue()
    yield q
