import os
import pytest
import datetime
import time
import multiprocessing
from random import randint
from uuid import uuid4
from pathlib import Path

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.misc.utility import display_message
from pade.core.agent import Agent_

os.sys.path.insert(0, os.getcwd())
from core.common import to_elementtree, to_string, dump # pylint: disable=import-error,no-name-in-module
from core.adc import AgenteDC, SubscreverACom, EnviarComando # pylint: disable=import-error,no-name-in-module
from core.acom import AgenteCom, EnvioDeDados, ReceberComando # pylint: disable=import-error,no-name-in-module
from information_model import SwitchingCommand as swc # pylint: disable=import-error

from tests.conftest import start_loop

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

    def stash_2(original, queue):
        def wrapper(self, message):
            # Joga valor na queue
            queue.put_nowait(message)
            # Modifica arquivos de IEDs para inserir valores de teste
            with open(Path(f'./core/ied/CH13.txt'), 'w') as file:
                file.write('XCBR BRKF')
            with open(Path(f'./core/ied/CH14.txt'), 'w') as file:
                file.write('XCBR')

            return original(self, message)
        return wrapper
    monkeypatch.setattr(SubscreverACom, 'handle_agree', stash_2(SubscreverACom.handle_agree, queue))

    monkeypatch.setattr(SubscreverACom, 'handle_inform', lambda self, message: dump(message.content))

def test_subscribe_to_ACom(run_ams, testar_recepcao_de_mensagem_1):
    
    sniffer = run_ams

    acom_aid = AID(f'acom@localhost:{randint(10000, 60000)}')
    acom = AgenteCom(acom_aid, 'S1', {'CH13': 'localhost', 'CH14': 'localhost'}, debug=True)
    acom.ams = sniffer.ams

    adc_aid = AID(f'agentdc@localhost:{randint(10000, 60000)}')
    adc = AgenteDC(adc_aid, 'S1', debug=True)
    adc.ams = sniffer.ams
    adc.subscribe_to(acom_aid)

    # Executa agentes em outro processo por 20 segundos
    start_loop([adc, acom])

    # Testar ordem de recepção de mensagens (performatives)
    assert queue.get_nowait().performative == 'subscribe'
    assert queue.get_nowait().performative == 'agree'

def test_dev():
    adc_aid = AID(f'agentdc@localhost:{randint(10000, 60000)}')
    adc = AgenteDC(adc_aid, 'S1', debug=True)
    