import os
os.sys.path.insert(0, os.getcwd()) 
# Adiciona ao Path a pasta raiz do projeto

from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.misc.utility import start_loop, display_message

from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaRequestProtocol

from core.common import AgenteSMAD
from uuid import uuid4

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
                # Cria conversation_id para continuar com estado do processo
                # mais tarde. Registra sessão com a mesma ID
                message.set_conversation_id(str(uuid4()))
                dados_recuperar = {"atividade": 'corrigindo falta', "Dados de sessão": 23423423}
                self.register_state(message.conversation_id, dados_recuperar)
                self.on_start()

            else:
                # Reenvia mensagem 5 segundos mais tarde
                print('Reenviar mensagem mais tarde...')
                self.agent.call_later(3.0, keep_trying)

        keep_trying()

    def register_state(self, state_id: str, state):
        # Registra o conversation_id da Mensagem, 
        # que será replicado pelo agente destinatário
        if not hasattr(self, 'states'):
            self.states = {}
        self.states[state_id] = state

    def retrieve_state(self, state_id):
        # Recupera o estado a partir do conversation_id
        return self.states.pop(state_id)

    def on_start(self):
        print('ComportamentoMandarMensagem::on_start')
        super().on_start()


    def handle_inform(self, message: ACLMessage):
        display_message(self.agent.aid.name, f'Recebida Inform. Conteúdo: {message.content}')
        state = self.retrieve_state(message.conversation_id)
        display_message(self.agent.aid.name, f'Estado a continuar: {state}')


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


class AgenteA(AgenteSMAD):
    def __init__(self, aid, debug=False):
        super().__init__(aid, debug)
        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.add_receiver(AID('agente_b@127.0.0.1:20001'))
        message.set_content('Oi')

        envio_beh = ComportamentoMandarMensagem(self, message)
        self.behaviours.append(envio_beh)


class AgenteB(AgenteSMAD):
    def __init__(self, aid, debug=False):
        super().__init__(aid, debug)
        receber_beh = ComportamentoReceberMensagem(self)
        self.behaviours.append(receber_beh)


if __name__ == "__main__":

    agente_a = AgenteA(AID('agente_a@127.0.0.1:20004'), True)
    agente_b = AgenteB(AID('agente_b@127.0.0.1:20001'), True)

    start_loop([agente_a, agente_b])
