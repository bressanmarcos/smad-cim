from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaRequestProtocol, TimedBehaviour

import xml.etree.ElementTree as ET
import lxml.etree as et

import information_model as im


class Conversa(FipaRequestProtocol):
    def __init__(self, agent: Agent, message=None, is_initiator=True):
        super(Conversa, self).__init__(
            agent, message, is_initiator=is_initiator)

    def handle_request(self, message: ACLMessage):
        im.o.parseString(ET.tostring(message))
        display_message(
            self.agent.aid.localname,
            "Recebi esse ID: {}".format(message.content)
        )

        reply_message = message.create_reply()
        reply_message.set_performative(ACLMessage.INFORM)
        reply_message.set_content("ACK!")
        self.agent.send(reply_message)

    def handle_inform(self, message: ACLMessage):
        display_message(
            self.agent.aid.localname, "Recebi esse inform: {}".format(message.content))


class Remetente(Agent):
    class Time(TimedBehaviour):
        def __init__(self, agent, time, message):
            super(Remetente.Time, self).__init__(agent, time)
            self.message = message

        def on_time(self):
            super(Remetente.Time, self).on_time()
            self.agent.send(self.message)

    def __init__(self, aid, message):
        super(Remetente, self).__init__(aid=aid)
        self.behaviours.append(Conversa(self, message, is_initiator=True))
        self.behaviours.append(Remetente.Time(self, 1.0, message))


class Destinatario(Agent):
    def __init__(self, aid):
        super(Destinatario, self).__init__(aid=aid)
        self.behaviours.append(Conversa(self, is_initiator=False))


if __name__ == "__main__":
    agentes = list()
    # Destinatário
    destinatario_aid = AID("destinatario@localhost:50000")
    destinatario_agente = Destinatario(destinatario_aid)
    agentes.append(destinatario_agente)
    # Mensagem de envio
    root = im.o.Outage_Type(mRID="CHAVE24")
    message = ACLMessage(ACLMessage.REQUEST)
    message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
    message.set_content(et.tostring(root.to_etree()))
    message.add_receiver(destinatario_aid)
    # Remetente
    remetente_aid = AID("remetente@localhost:50001")
    remetente_agente = Remetente(remetente_aid, message)
    agentes.append(remetente_agente)

    start_loop(agentes)
