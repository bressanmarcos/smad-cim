from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaRequestProtocol, TimedBehaviour
from pade.misc.utility import display_message

from core.common import *

import information_model as im
import xml.etree.ElementTree as ET


class LogDeEventos(FipaRequestProtocol):
    def __init__(self, agent):
        super(LogDeEventos, self).__init__(agent, is_initiator=False)
        self.agent: AgenteDF

    def handle_request(self, message: ACLMessage):
        super(LogDeEventos, self).handle_request(message)
        # Executa a função que corresponde à ontologia da mensagem
        response = getattr(self, message.ontology)(message)
        # RESPONDER MENSAGEM
        message = message.create_reply()
        message.set_performative(ACLMessage.INFORM)
        if response:
            message.set_content(response)
        self.agent.send(message)

    # Funções chamadas de acordo com a ontologia da mensagem
    def Outage(self, message):
        document = im.o.parseString(to_string(message.content), silence=True)
        display_message(
            self.agent.aid.localname,
            "Capturei essa chave: {}".format(document.get_mRID())
        )


class AgenteDF(AgenteSMAD):
    def __init__(self, aid, substation, debug=False):
        super(AgenteDF, self).__init__(aid, substation, debug)
        self.behaviours.append(
            LogDeEventos(self)
        )
