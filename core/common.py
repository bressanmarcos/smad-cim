from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
import xml.etree.ElementTree as ET
import lxml.etree as lET


def to_elementtree(document, name_):
    etree = document.to_etree(name_=name_)
    try:
        return ET.fromstring(lET.tostring(etree))
    except:
        return etree


def to_string(element):
    try:
        return ET.tostring(element)
    except:
        return lET.tostring(element)

class AgenteSMAD(Agent):
    def __init__(self, aid, subestacao, debug=False):
        super().__init__(aid, debug)
        self.subestacao = subestacao
