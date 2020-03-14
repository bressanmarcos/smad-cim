from pade.misc.utility import display_message, start_loop
from pade.acl.aid import AID
import core
import information_model as im

"""
class Conversa(FipaRequestProtocol):
    def __init__(self, agent: Agent, message=None, is_initiator=True):
        super(Conversa, self).__init__(
            agent, message, is_initiator=is_initiator)

    def handle_request(self, message: ACLMessage):
        root = im.Outagesubs.parseString(
            ET.tostring(message.content), silence=True)
        mRID = root.get_mRID()

        display_message(
            self.agent.aid.localname, "Recebi esse ID: {}".format(mRID))

        reply_message = message.create_reply()
        reply_message.set_performative(ACLMessage.INFORM)
        reply_message.set_content("ACK!")
        self.agent.send(reply_message)

    def handle_inform(self, message: ACLMessage):
        display_message(
            self.agent.aid.localname, "Recebi esse inform: {}".format(message.content))
"""

if __name__ == "__main__":
    lista_agentes = [
        # Agente Comunicação
        core.AgenteCom(AID('agente_com'), 'S1',
                       './config_TRIP_S1.txt', 'agente_dc'),
        core.AgenteDC(AID('agente_dc'), 'S1'),
        core.AgenteDF(AID('agente_df'), 'S1'),
    ]
    start_loop(lista_agentes)
