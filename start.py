from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.misc.utility import start_loop, display_message

from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaRequestProtocol

# importando agentes
from core.adc import AgenteDC
from core.acom import AgenteCom
from core.an import AgenteN

from random import randint

def config_agents():
    # Criterios para Agente Negociacao
    criterios = {"chaveamentos": False,
                 "carreg_SE": True,
                 "perdas": False,
                 "carga_prior": False}

    enderecos_S1 = {"CH1": "192.168.0.101",
                    "CH2": "192.168.0.102",
                    "CH3": "192.168.0.103",
                    "CH6": "192.168.0.106",
                    "CH7": "192.168.0.107",
                    "CH8": "192.168.0.108",
                    "CH9": "192.168.0.109",
                    "CH10": "192.168.0.110",
                    "CH11": "192.168.0.111",
                    "CH13": "192.168.0.113",
                    "CH14": "192.168.0.114",
                    "CH15": "192.168.0.115",
                    "CH16": "192.168.0.116"}
    enderecos_S2 = {"CH4": "192.168.0.104",
                    "CH5": "192.168.0.105",
                    "CH3": "192.168.0.103",
                    "CH8": "192.168.0.108",
                    "CH11": "192.168.0.111",
                    "CH12": "192.168.0.112",
                    "CH16": "192.168.0.116"}

    agentes = list()

    # Agentes da Subestacao 01
    adc1 = AgenteDC(AID("S1_adc@localhost:4001"), "S1")
    adc1.ams = {"name": "localhost", "port": 8000}
    agentes.append(adc1)

    acom1 = AgenteCom(AID("S1_acon@localhost:4004"), "S1", enderecos_S1)
    acom1.ams = {"name": "localhost", "port": 8000}
    agentes.append(acom1)

    aneg1 = AgenteN(AID("S1_ANeg@localhost:4006"), subestacao="S1")
    aneg1.ams = {"name": "localhost", "port": 8000}
    agentes.append(aneg1)

    # Agentes da SE2
    adc2 = AgenteDC(AID("S2_ADiag@localhost:4007"), subestacao="S2")
    adc2.ams = {"name": "localhost", "port": 8000}
    agentes.append(adc2)

    acom2 = AgenteCom(AID("S2_acom@localhost:4011"), "S2", enderecos_S2)
    acom2.ams = {"name": "localhost", "port": 8000}
    agentes.append(acom2)

    aneg2 = AgenteN(AID("S2_ANeg@localhost:4013"), "S1")
    aneg2.ams = {"name": "localhost", "port": 8000}
    agentes.append(aneg2)

    return agentes


class ComportamentoMandarMensagem(FipaRequestProtocol):
    def __init__(self, agent, message=None, is_initiator=True):
        super().__init__(agent, message, is_initiator)
        self.agent: Agent

        def keep_trying():
            # Se o ACom já estiver na tabela
            if hasattr(self.agent, 'agentInstance') and all(
                    receiver.name in self.agent.agentInstance.table for receiver in message.receivers):
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

    start_loop(config_agents())
