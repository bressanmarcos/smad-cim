"""Contém funções e classes úteis
"""

import os
os.sys.path.insert(0, os.getcwd()) 
# Adiciona ao Path a pasta raiz do projeto

import xml.etree.ElementTree as ET
import lxml.etree as lET
from xml.dom.minidom import parseString

from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.misc.utility import display_message

from information_model import SwitchingCommand as swc

def to_elementtree(document, name_=None):
    """Converte elemento do generateDS em ElementTree
    """
    etree = document.to_etree() if name_ == None else document.to_etree(name_=name_)
    try:
        return ET.fromstring(lET.tostring(etree))
    except:
        return etree


def to_string(elementtree):
    """Converte um ElementTree em string"""
    try:
        return ET.tostring(elementtree)
    except:
        return lET.tostring(elementtree)


def dump(elementtree):
    """Imprime ElementTree no stdout 
    """
    rough_string = to_string(elementtree)
    reparsed = parseString(rough_string)
    print(reparsed.toprettyxml(indent=' '*4))

def validate(information_object):
    gds = swc.GdsCollector_()
    information_object.validate_(gds, recursive=True)
    if len(gds.get_messages()) != 0:
        for message in gds.get_messages():
            raise Warning(message)

class AgenteSMAD(Agent):
    def __init__(self, aid, subestacao, debug=False):
        super().__init__(aid, debug)
        # Identifica a subestação a que pertence o agente
        self.subestacao = subestacao
        # Variável de estados guardados
        self.sessions = {}

        display_message(self.aid.name, "Agente instanciado")

    def register_state(self, session_id: str, session_state: dict, awaits=1):
        # Registra o conversation_id da Mensagem, 
        # para manter estado
        self.sessions[session_id] = (session_state, awaits)

    def retrieve_state(self, session_id: str):
        # Recupera o estado a partir do conversation_id
        session_state, awaits = self.sessions.pop(session_id)
        awaits -= 1
        # Só apaga estado quando a última mensagem for recebida
        if awaits != 0:
            self.register_state(session_id, session_state, awaits)
        return session_state, awaits

    def async_send(self, message: ACLMessage, callbacks: dict, awaits=1):
        self.register_state(message.conversation_id, callbacks, awaits)
        self.send(message)

    def continue_flow(self, message: ACLMessage):
        session_state, awaits = self.retrieve_state(message.conversation_id)
        if awaits == 0:
            session_state[message.performative]()

    def send_until(self, message, tries=10, interval=2.0):
        def later(tries, interval):
            if hasattr(self, 'agentInstance') and all(receiver.name in self.agentInstance.table for receiver in message.receivers):
                # Envia mensagem
                self.send(message)
            else:
                # Reenvia mensagem mais tarde
                self.call_later(interval, lambda: later(tries-1, interval))
        later(tries, interval)
