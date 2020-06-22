import pytest
import datetime
import time
import multiprocessing
from random import random
from uuid import uuid4

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.misc.utility import display_message
from pade.core.agent import Agent_
from pade.misc.utility import start_loop

import sys
sys.path.insert(0, '../')
from core.common import to_elementtree, to_string, dump # pylint: disable=import-error,no-name-in-module
from core.adc import AgenteDC, SubscreverACom # pylint: disable=import-error,no-name-in-module
from core.acom import AgenteCom, EnvioDeDados # pylint: disable=import-error,no-name-in-module
from information_model import SwitchingCommand as swc # pylint: disable=import-error

@pytest.fixture
def delete_call_later(monkeypatch):
    """Impede o uso de call_later"""
    monkeypatch.setattr(Agent_, "call_later", lambda self, time, method, *args: 1)

@pytest.fixture()
def mock_debug_send_message(monkeypatch):
    """Evita o envio de mensagem pelo ator, 
    Em vez disso, imprime na tela a mensagem que seria enviada
    """
    def stack_send(original_send):
        def wrap_send(self, message, receivers):
            dump(message)
            return original_send(self, message, receivers)
        return wrap_send

    monkeypatch.setattr(Agent_, '_send', stack_send(Agent_._send))

queue = []
@pytest.fixture
def injetar_queue(monkeypatch):
    global queue
    def stash(original, queue):
        def wrapper(self, message):
            queue.append(message.performative)
            print(queue)
            return original(self, message)
        return wrapper

    monkeypatch.setattr(EnvioDeDados, 'handle_subscribe', stash(EnvioDeDados.handle_subscribe, queue))
    monkeypatch.setattr(SubscreverACom, 'handle_agree', stash(SubscreverACom.handle_agree, queue))

def test_subscribe(with_ams, injetar_queue):
    def process():
        sniffer = with_ams
        acom = AgenteCom(AID('acom@localhost:9001'), 'S1', debug=True)
        acom.ams = sniffer.ams
        adc = AgenteDC(AID('agentdc@localhost:9000'), 'S1', debug=True)
        adc.subscribe_to(AID('acom@localhost:9001'))
        adc.ams = sniffer.ams
        start_loop([sniffer, adc, acom])

    p = multiprocessing.Process(target=process)
    p.start(), time.sleep(20), p.terminate()


