import datetime
from random import random
from uuid import uuid4

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import (FipaRequestProtocol,
                                       FipaSubscribeProtocol, TimedBehaviour)
from pade.misc.utility import display_message

from core.common import AgenteSMAD, to_elementtree, to_string, dump
from core.acom import AgenteCom

import sys
sys.path.insert(0, '../')
from information_model import SwitchingCommand as swc

class SubscreverACom(FipaSubscribeProtocol):
    def __init__(self, agent: AgenteSMAD, message=None, is_initiator=True):
        super().__init__(agent, message=message, is_initiator=is_initiator)
        
    def handle_agree(self, message):
        display_message(self.agent.aid.name, 'Inscrito em ACom')

    def handle_inform(self, message: ACLMessage):    
        # TODO: Funções chamadas de acordo com a ontologia da mensagem
        def outage(message):
            display_message(self.agent.aid.name, 'Mensagem INFORM recebida de %s' % message.sender.localname)
            print(message.content)

        # Chama a função que corresponde à ontologia da mensagem
        try:
            locals()[message.ontology](message)
        except:
            display_message(self.agent.aid.name, 'Mensagem não reconhecida')
            not_understood = message.create_reply()
            not_understood.set_performative(ACLMessage.NOT_UNDERSTOOD)
            self.agent.send(not_understood)

class EnviarComando(FipaRequestProtocol):
    def __init__(self, agent):
        super().__init__(agent, message=None, is_initiator=True)

    def handle_not_understood(self, message: ACLMessage):
        display_message(self.agent.aid.name, 'Mensagem não compreendida')
        display_message(self.agent.aid.name, message.content)

    def handle_failure(self, message: ACLMessage):
        display_message(self.agent.aid.name, 'Falha em execução de comando')
        display_message(self.agent.aid.name, message.content)

    def handle_inform(self, message: ACLMessage):
        display_message(self.agent.aid.name, 'Chaveamento realizado')
        display_message(self.agent.aid.name, message.content)

class AgenteDC(AgenteSMAD):
    def __init__(self, aid, subestacao, debug=False):
        super().__init__(aid, subestacao, debug)
        self.behaviours.append(EnviarComando(self))

    def subscribe_to(self, acom_aid: AID):
        """Subcribe to ``AgenteCom``"""
        message = ACLMessage(ACLMessage.SUBSCRIBE)
        message.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
        message.add_receiver(acom_aid)
        self.subscribe_behaviour = SubscreverACom(self, message, is_initiator=True)
        self.behaviours.append(self.subscribe_behaviour)
        def later():
            if hasattr(self, 'agentInstance') and acom_aid.name in self.agentInstance.table:
                # Envia mensagem
                self.subscribe_behaviour.on_start()
            else:
                # Reenvia mensagem mais tarde
                self.call_later(5.0, later)
        later()
