import pytest
import datetime
import time
from random import random
import multiprocessing
from uuid import uuid4

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.misc.utility import display_message
from pade.core.agent import Agent_

import sys
sys.path.insert(0, '../')
from core.common import to_elementtree, to_string, dump, validate # pylint: disable=import-error,no-name-in-module
from core.acom import AgenteCom, ReceberComando # pylint: disable=import-error,no-name-in-module
from information_model import SwitchingCommand as swc # pylint: disable=import-error

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
    enderecos_S2 = {"CH4": "192.168.0.104",
                    "CH5": "192.168.0.105",
                    "CH3": "192.168.0.103",
                    "CH8": "192.168.0.108",
                    "CH11": "192.168.0.111",
                    "CH12": "192.168.0.112",
                    "CH16": "192.168.0.116"}
    enderecos_S3 = {"CH17": "192.168.0.117",
                    "CH18": "192.168.0.118",
                    "CH16": "192.168.0.116"}

    acom = AgenteCom(AID('acom1@localhost:9000'), 'S1', enderecos_S1)

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
