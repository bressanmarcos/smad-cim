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
        self.subestacao = subestacao
        display_message(self.aid.name, "Agente instanciado")

    def send_until(self, message, tries=10, interval=2.0):
        def later(tries, interval):
            if hasattr(self, 'agentInstance') and all(receiver.name in self.agentInstance.table for receiver in message.receivers):
                # Envia mensagem
                self.send(message)
            else:
                # Reenvia mensagem mais tarde
                self.call_later(interval, lambda: later(tries-1, interval))
        later(tries, interval)

