import os
os.sys.path.insert(0, os.getcwd()) 
# Adiciona ao Path a pasta raiz do projeto

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
                file.write('XCBR')
            with open(Path(f'./core/ied/CH14.txt'), 'w') as file:
                file.write('XCBR')

            return original(self, message)
        return wrapper
    monkeypatch.setattr(SubscreverACom, 'handle_agree', stash_2(SubscreverACom.handle_agree, queue))
    #monkeypatch.setattr(SubscreverACom, 'handle_inform', lambda self, message: dump(message.content))


def test_subscribe_to_ACom(run_ams, testar_recepcao_de_mensagem_1):
    sniffer = run_ams

    acom_aid = AID(f'acom@localhost:{randint(10000, 60000)}')
    acom = AgenteCom(acom_aid, 'S1', {'CH13': 'localhost', 'CH14': 'localhost'}, debug=True)
    acom.ams = sniffer.ams

    adc_aid = AID(f'agentdc@localhost:{randint(10000, 60000)}')
    adc = AgenteDC(adc_aid, 'S1', debug=True)
    adc.ams = sniffer.ams
    
    adc.subscrever_a(acom.aid)

    # Executa agentes em outro processo por 20 segundos
    start_loop([adc, acom])

    # Testar ordem de recepção de mensagens (performatives)
    assert queue.get_nowait().performative == 'subscribe'
    assert queue.get_nowait().performative == 'agree'

def test_dev(run_ams):
    sniffer = run_ams
    # Testando passo a passo do ADCa até recomposição
    enderecos_S1 = {"CH1": "192.168.0.101",
                    "CH2": "192.168.0.102",
                    "CH3": "192.168.0.103",
                    "CH6": "192.168.0.106",
                    "CH7": "192.168.0.107",
                    "CH8": "192.168.0.108",
                    "CH9": "192.168.0.109",
                    "CH10": "192.168.0.110",
                    "CH11": "192.168.0.111",
                    "CH13": "192.168.0.113",
                    "CH14": "192.168.0.114",
                    "CH15": "192.168.0.115",
                    "CH16": "192.168.0.116"}
    acom = AgenteCom(AID('agentecom@localhost:60003'), 'S1', enderecos_S1)
    acom.ams = sniffer.ams

    start_loop([acom, sniffer], 100000.0)
    
    
