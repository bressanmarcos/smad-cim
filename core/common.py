"""Contém funções e classes úteis
"""

import os
os.sys.path.insert(0, os.getcwd()) 
# Adiciona ao Path a pasta raiz do projeto

from time import time
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
        # Variável de estados guardados para uso de  send e async_receive
        self.sessions = {}

        display_message(self.aid.name, "Agente instanciado")

    def send(self, message: ACLMessage, callback=None):
        """Registra callback antes de enviar mensagem"""
        
        if callback is not None:
            self.sessions[message.conversation_id] = callback

        # Envia mensagem
        super().send(message)
        
        # Deleta key após timeout
        if callback is not None:
            def delete_key():
                try:
                    del self.sessions[message.conversation_id]
                except KeyError:
                    pass
            self.call_later(600, delete_key)

    def react(self, message: ACLMessage):
        """Recupera callback depois de receber mensagem"""

        # Receber mensagem e executar behaviours
        super().react(message)

        # Chamar callback
        if message.conversation_id in self.sessions:
            callback = self.sessions[message.conversation_id]
            callback(message)

    def send_until(self, message, tries=10, interval=2.0):
        """Continua a reenviar mensagem até que todos os destinatários
        estejam disponíveis"""

        def later(tries, interval):
            if tries == 0:
                return
            # A tabela do agente deve conter todos os destinatários antes do envio
            if hasattr(self, 'agentInstance') and all(receiver.name in self.agentInstance.table for receiver in message.receivers):
                # Envia mensagem agora
                self.send(message)
            else:
                # Reenvia mensagem mais tarde
                self.call_later(interval, lambda: later(tries-1, interval))
        later(tries, interval)
