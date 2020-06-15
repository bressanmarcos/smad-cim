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
    debug = False
    lista_agentes = [
        core.AgenteCom(AID('agente_com'), 'S1', debug=debug),
        core.AgenteCom(AID('agente_com2'), 'S1', debug=debug),
        # Agente de Diagnóstico e Configuração
        core.AgenteDC(AID('agente_dc'), 'S1', debug=debug),
    ]
    start_loop(lista_agentes)
