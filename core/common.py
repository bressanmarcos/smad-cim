"""Contém funções e classes úteis
"""

from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
import xml.etree.ElementTree as ET
import lxml.etree as lET
from xml.dom.minidom import parseString


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


class AgenteSMAD(Agent):
    def __init__(self, aid, subestacao, debug=False):
        super().__init__(aid, debug)
        self.subestacao = subestacao
