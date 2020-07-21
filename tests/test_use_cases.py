import os
os.sys.path.insert(0, os.getcwd()) 
# Adiciona ao Path a pasta raiz do projeto

import pytest
import datetime
import time
import multiprocessing
from random import randint
from uuid import uuid4

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.misc.utility import display_message
from pade.core.agent import Agent_

from core.common import to_elementtree, to_string, dump # pylint: disable=import-error,no-name-in-module
from core.adc import AgenteDC, SubscreverACom, EnviarComando # pylint: disable=import-error,no-name-in-module
from core.acom import AgenteCom, EnvioDeDados, ReceberComando # pylint: disable=import-error,no-name-in-module
from core.ied import IED  # pylint: disable=import-error,no-name-in-module
from information_model import SwitchingCommand as swc # pylint: disable=import-error

from tests.conftest import start_loop

queue = None
@pytest.fixture(scope='function')
def testar_recepcao_de_mensagem_2(monkeypatch):
    """Injeta um retorno das mensagens recebidas pelos
    comandos EnviarComando::handle_inform do ADC e 
    ReceberComando::handle_request do ACom
    Valores podem ser recuperados pela Fila ``queue``"""
    global queue
    queue = multiprocessing.Queue()
    def stash(original, queue):
        """Executa função original, mas insere seus
        argumentos antes na queue."""
        def wrapper(self, *args):
            queue.put(args)
            return original(self, *args)
        return wrapper
    def do_nothing(queue):
        """Somente insere na queue os argumentos"""
        def wrapper(self, *args):
            queue.put(args)
            return
        return wrapper
    monkeypatch.setattr(EnviarComando, 'handle_inform', do_nothing(queue))
    monkeypatch.setattr(ReceberComando, 'handle_request', stash(ReceberComando.handle_request, queue))
    monkeypatch.setattr(IED, 'operate', stash(IED.operate, queue))

def test_UC_Comando_de_Chaves_Cenario_Principal(run_ams, testar_recepcao_de_mensagem_2):

    sniffer = run_ams
    # Define lista de chaves do ACom
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
    # Definir agentes ADC e ACom
    acom_aid = AID(f'acom@localhost:{randint(10000, 60000)}')
    adc_aid = AID(f'agentdc@localhost:{randint(10000, 60000)}')
    acom = AgenteCom(acom_aid, 'S1', enderecos_IEDs=enderecos_S1, debug=True)
    adc = AgenteDC(adc_aid, 'S1', debug=True)
    # Configurar endereço do AMS de teste
    acom.ams = sniffer.ams
    adc.ams = sniffer.ams
    # Adicionar ACom às incrições de ADC
    adc.subscrever_a(acom_aid)
    # Antecede inscrição para mandar comando (não necessário em produção)
    adc.assinaturas = [acom_aid]
    # Criar objeto a enviar
    lista_de_comandos = {'CH14': 'open', 'CH13': 'close'}
    # Enviar mensagem
    adc.enviar_comando_de_chave(
        lista_de_comandos=lista_de_comandos, 
        proposito='isolation',
        conversation_id = str(uuid4()))

    # Executa agentes em outro processo por 20 segundos
    start_loop([adc, acom])

    # Testar ordem de recepção de mensagens (performatives)
    assert queue.get_nowait()[0].performative == 'request'
    assert queue.get_nowait()[0] == 'open'
    assert queue.get_nowait()[0] == 'close'
    assert queue.get_nowait()[0].performative == 'inform'

    