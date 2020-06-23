from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.misc.utility import start_loop, display_message

from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaRequestProtocol

class ComportamentoMandarMensagem(FipaRequestProtocol):
    def __init__(self, agent, message=None, is_initiator=True):
        super().__init__(agent, message, is_initiator)
        self.agent: Agent
        def keep_trying():
            # Se o ACom já estiver na tabela
            if hasattr(self.agent, 'agentInstance') and all(receiver.name in self.agent.agentInstance.table for receiver in message.receivers):
                # Envia mensagem
                self.on_start()
            else:
                # Reenvia mensagem 5 segundos mais tarde
                self.agent.call_later(5.0, keep_trying)
        keep_trying()

    def handle_inform(self, message: ACLMessage):
        display_message(self.agent.aid.name, f'Recebida Inform. Conteúdo: {message.content}')

class ComportamentoReceberMensagem(FipaRequestProtocol):
    def __init__(self, agent, message=None, is_initiator=False):
        super().__init__(agent, message, is_initiator)

    def handle_request(self, message: ACLMessage):
        display_message(self.agent.aid.name, f'Recebido Request. Conteúdo: {message.content}')
        # Mensagem de resposta
        message_reply = message.create_reply()
        message_reply.set_performative(ACLMessage.INFORM)
        message_reply.set_content('Tudo bem?')
        self.agent.send(message_reply)
        
class AgenteA(Agent):
    def __init__(self, aid, debug=False):
        super().__init__(aid, debug)
        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.add_receiver(AID('agente_b@127.0.0.1:20000'))
        message.set_content('Oi')

        envio_beh = ComportamentoMandarMensagem(self, message)
        self.behaviours.append(envio_beh)

class AgenteB(Agent):
    def __init__(self, aid, debug=False):
        super().__init__(aid, debug)
        receber_beh = ComportamentoReceberMensagem(self)
        self.behaviours.append(receber_beh)

if __name__ == "__main__":
    a = AgenteA(AID('elifranio@127.0.0.1:10000'), debug=True)
    b = AgenteB(AID('agente_b@127.0.0.1:20000'), debug=True)

    start_loop([a, b])