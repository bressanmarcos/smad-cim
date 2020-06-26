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
from core.adc import AgenteDC, SubscreverACom, EnviarComando # pylint: disable=import-error,no-name-in-module
from core.acom import AgenteCom, EnvioDeDados, ReceberComando # pylint: disable=import-error,no-name-in-module
from information_model import SwitchingCommand as swc # pylint: disable=import-error

queue = None
@pytest.fixture(scope='function')
def testar_recepcao_de_mensagem_1(monkeypatch):
    """Injeta um retorno das mensagens recebidas pelos
    comandos EnvioDeDados::handle_subscribe do ACom e 
    SubscreverACom::handle_agree do ADC.
    Valores podem ser recuperados pela Fila ``queue``"""
    global queue
    queue = multiprocessing.Queue()
    def stash(original, queue):
        def wrapper(self, message):
            queue.put_nowait(message)
            return original(self, message)
        return wrapper

    monkeypatch.setattr(EnvioDeDados, 'handle_subscribe', stash(EnvioDeDados.handle_subscribe, queue))
    monkeypatch.setattr(SubscreverACom, 'handle_agree', stash(SubscreverACom.handle_agree, queue))

def test_subscribe_to_ACom(run_ams, testar_recepcao_de_mensagem_1):
    def parallel_process():
        sniffer = run_ams
        acom = AgenteCom(AID('acom@localhost:9001'), 'S1', debug=True)
        acom.ams = sniffer.ams
        adc = AgenteDC(AID('agentdc@localhost:9000'), 'S1', debug=True)
        adc.subscribe_to(AID('acom@localhost:9001'))
        adc.ams = sniffer.ams
        start_loop([sniffer, adc, acom])

    p = multiprocessing.Process(target=parallel_process)
    p.start(), time.sleep(20.0), p.kill()

    # Testar ordem de recepção de mensagens (performatives)
    assert queue.get_nowait().performative == 'subscribe'
    assert queue.get_nowait().performative == 'agree'


