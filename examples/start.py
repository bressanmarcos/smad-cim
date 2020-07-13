import os
os.sys.path.append(os.getcwd())

from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.misc.utility import start_loop, display_message

from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaRequestProtocol

from random import randint

class ComportamentoMandarMensagem(FipaRequestProtocol):
    def __init__(self, agent, message=None, is_initiator=True):
        super().__init__(agent, message, is_initiator)
        self.agent: Agent
        print('ComportamentoMandarMensagem::__init__')
        def keep_trying():
            # Se o ACom já estiver na tabela
            if hasattr(self.agent, 'agentInstance') and all(receiver.name in self.agent.agentInstance.table for receiver in message.receivers):
                # Envia mensagem
                print('Enviar mensagem agora...')
                self.on_start()
            else:
                # Reenvia mensagem 5 segundos mais tarde
                print('Reenviar mensagem mais tarde...')
                self.agent.call_later(3.0, keep_trying)

        keep_trying()

    def on_start(self):
        print('ComportamentoMandarMensagem::on_start')
        super().on_start()


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
        message.add_receiver(AID('agente_b@127.0.0.1:20001'))
        message.set_content('Oi')

        envio_beh = ComportamentoMandarMensagem(self, message)
        self.behaviours.append(envio_beh)


class AgenteB(Agent):
    def __init__(self, aid, debug=False):
        super().__init__(aid, debug)
        receber_beh = ComportamentoReceberMensagem(self)
        self.behaviours.append(receber_beh)


if __name__ == "__main__":

    agente_a = AgenteA(AID('agente_a@127.0.0.1:20004'), True)
    agente_b = AgenteB(AID('agente_b@127.0.0.1:20001'), True)

    start_loop([agente_a, agente_b])
