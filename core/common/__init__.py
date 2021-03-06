"""Contém funções e classes úteis
"""

import os
import xml.etree.ElementTree as ET
from time import time
from random import randint
from xml.dom.minidom import parseString

import lxml.etree as lET
from information_model import SwitchingCommand as swc
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.misc.utility import display_message
from pade.plus.agent import ImprovedAgent

def randomport():
    return randint(8000, 60000)

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


class AgenteSMAD(ImprovedAgent):
    def __init__(self, aid, substation, debug=False):
        super().__init__(aid, debug)
        # Identifica a subestação a que pertence o agente
        self.substation = substation
