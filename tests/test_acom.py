import datetime
import time
from random import random
from uuid import uuid4

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import (FipaRequestProtocol,
                                       FipaSubscribeProtocol, TimedBehaviour)
from pade.misc.utility import display_message

import sys
sys.path.insert(0, '../')
from core.common import AgenteSMAD, to_elementtree, to_string, dump
from core.acom import AgenteCom
from information_model import SwitchingCommand as swc

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
# Exemmplo de Arquivo para ser recebido pelo ACOM
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

# Monta envelope de mensagem ACL
message = ACLMessage(performative=ACLMessage.INFORM)
message.set_ontology('SwitchingCommand')
message.set_content(to_elementtree(root))

# Simula recepção de mensagem
acom.behaviours[1].handle_request(message)       

