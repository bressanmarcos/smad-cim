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
def testar_recepcao_de_mensagem_2(monkeypatch):
    """Injeta um retorno das mensagens recebidas pelos
    comandos EnviarComando::handle_inform do ADC e 
    ReceberComando::handle_request do ACom
    Valores podem ser recuperados pela Fila ``queue``"""
    global queue
    queue = multiprocessing.Queue()
    def stash(original, queue):
        def wrapper(self, message):
            queue.put_nowait(message.performative)
            return original(self, message)
        return wrapper

    monkeypatch.setattr(EnviarComando, 'handle_inform', stash(EnviarComando.handle_inform, queue))
    monkeypatch.setattr(ReceberComando, 'handle_request', stash(ReceberComando.handle_request, queue))

def test_UC_Comando_de_Chaves_Cenario_Principal(run_ams, testar_recepcao_de_mensagem_2):

    def parallel_process():
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
        acom = AgenteCom(AID('acom@localhost:9001'), 'S1', enderecos_IEDs=enderecos_S1, debug=True)
        adc = AgenteDC(AID('agentdc@localhost:9000'), 'S1', debug=True)
        # Configurar endereço do AMS de teste
        acom.ams = sniffer.ams
        adc.ams = sniffer.ams
        # Criar objeto a enviar
        swt13 = swc.ProtectedSwitch(
            mRID='CH13', name='Switch que protege minha casa')
        swt14 = swc.ProtectedSwitch(
            mRID='CH14', name='Switch do portão')
        acao1 = swc.SwitchAction(
            executedDateTime=datetime.datetime.now(),
            isFreeSequence=False,
            issuedDateTime=datetime.datetime.now(),
            kind=swc.SwitchActionKind.CLOSE,
            plannedDateTime=datetime.datetime.now(),
            sequenceNumber=1,
            OperatedSwitch=swt13)
        acao0 = swc.SwitchAction(
            executedDateTime=datetime.datetime.now(),
            isFreeSequence=False,
            issuedDateTime=datetime.datetime.now(),
            kind=swc.SwitchActionKind.OPEN,
            plannedDateTime=datetime.datetime.now(),
            sequenceNumber=0,
            OperatedSwitch=swt14)
        plano = swc.SwitchingPlan(
            mRID=str(uuid4()), 
            createdDateTime=datetime.datetime.now(),
            name='Plano de Teste', 
            purpose=swc.Purpose.COORDINATION, 
            SwitchAction=[acao1, acao0])
        root = swc.SwitchingCommand(SwitchingPlan=plano)
        # Enviar mensagem
        adc.enviar_comando_de_chave(switching_command=root, acom_aid=AID('acom@localhost:9001'))
        # Rodar agentes
        start_loop([sniffer, adc, acom])

    p = multiprocessing.Process(target=parallel_process)
    p.start(), time.sleep(20.0), p.kill()

    # Testar ordem de recepção de mensagens (performatives)
    assert queue.get_nowait() == 'request'
    assert queue.get_nowait() == 'inform'
    