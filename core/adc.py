from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaRequestProtocol, FipaSubscribeProtocol, TimedBehaviour
from pade.misc.utility import display_message

from core.common import *

import information_model as im
import xml.etree.ElementTree as ET

class SubscriptionACom(FipaSubscribeProtocol):
    def __init__(self, agent: AgenteSMAD, message=None, is_initiator=True):
        super().__init__(agent, message=message, is_initiator=is_initiator)
        self.on_start()

    def handle_agree(self, message):
        display_message(self.agent.aid.name, 'Fui aceito!')

    def handle_inform(self, message: ACLMessage):    
        # Funções chamadas de acordo com a ontologia da mensagem
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



class AgenteDC(AgenteSMAD):
    def __init__(self, aid, subestacao, debug=False):
        super().__init__(aid, subestacao, debug)
        self.call_later(10, self.later)

    def later(self):
        display_message(self.aid.name, 'Vou me subscrever com o ACom')
        subscribe_message = ACLMessage(ACLMessage.SUBSCRIBE)
        subscribe_message.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
        for agent_name, agent_address in self.agentInstance.table.items():
            if agent_name.startswith('agente_com'):
                subscribe_message.add_receiver(agent_address)

        self.behaviours = [
            SubscriptionACom(self, subscribe_message),
        ]