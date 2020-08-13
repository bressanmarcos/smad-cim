import os
os.sys.path.insert(0, os.getcwd()) 
# Adiciona ao Path a pasta raiz do projeto

import pytest
import datetime
import time
from random import randint
import multiprocessing
from uuid import uuid4

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.misc.utility import display_message
from pade.core.agent import Agent_

from core.common import to_elementtree, to_string, dump, validate # pylint: disable=import-error,no-name-in-module
from core.acom import AgenteCom, ReceberComando # pylint: disable=import-error,no-name-in-module
from information_model import SwitchingCommand as swc # pylint: disable=import-error

from tests.conftest import start_loop

queue = None
@pytest.fixture(scope='function')
def debug_comandar_chave(monkeypatch):
    """Injeta um retorno das mensagens recebidas pela função
    ``comandar_chave`` na fila ``queue``"""
    global queue
    queue = multiprocessing.Queue()
    def stack_comandar_chave(comandar_chave):
        def wrapper_comandar_chave(self, switchId=None, action='open'):
            queue.put_nowait((switchId, action))
            comandar_chave(self, switchId, action)
        return wrapper_comandar_chave

    monkeypatch.setattr(AgenteCom, 'comandar_chave', stack_comandar_chave(AgenteCom.comandar_chave))

def test_handle_request(deactivate_send_message, debug_comandar_chave):
    """Testa (sem Rede) o ReceberComando::handle_request do ACom"""
    enderecos_S1 = {"CH1": ("localhost", 50000+1),
                    "CH2": ("localhost", 50000+2),
                    "CH3": ("localhost", 50000+3),
                    "CH6": ("localhost", 50000+6),
                    "CH7": ("localhost", 50000+7),
                    "CH8": ("localhost", 50000+8),
                    "CH9": ("localhost", 50000+9),
                    "CH10": ("localhost", 50000+10),
                    "CH11": ("localhost", 50000+11),
                    "CH13": ("localhost", 50000+13),
                    "CH14": ("localhost", 50000+14),
                    "CH15": ("localhost", 50000+15),
                    "CH16": ("localhost", 50000+16)}
    enderecos_S2 = {"CH4": ("localhost", 50000+4),
                    "CH5": ("localhost", 50000+5),
                    "CH3": ("localhost", 50000+3),
                    "CH8": ("localhost", 50000+8),
                    "CH11": ("localhost", 50000+11),
                    "CH12": ("localhost", 50000+12),
                    "CH16": ("localhost", 50000+16)}
    enderecos_S3 = {"CH17": ("localhost", 50000+17),
                    "CH18": ("localhost", 50000+18),
                    "CH16": ("localhost", 50000+16)}

    acom = AgenteCom(AID(f'acom1@localhost:{randint(10000, 60000)}'), 'S1', enderecos_S1)

    #################################################
    # Exemplo de Arquivo para ser recebido pelo ACOM
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
    validate(root)
    # Monta envelope de mensagem ACL
    message = ACLMessage(performative=ACLMessage.REQUEST)
    message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
    message.set_ontology('SwitchingCommand')
    message.set_content(to_elementtree(root))

    # Simula recepção de mensagem
    acom.behaviours[1].handle_request(message)      

    # Testa valores retornados
    assert queue.get_nowait() == ('CH14', swc.SwitchActionKind.OPEN)
    assert queue.get_nowait() == ('CH13', swc.SwitchActionKind.CLOSE)
