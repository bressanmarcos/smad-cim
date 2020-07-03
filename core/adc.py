import datetime
from random import random
from uuid import uuid4

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import (FipaRequestProtocol, FipaSubscribeProtocol, FipaContractNetProtocol)
from pade.misc.utility import display_message

from core.common import AgenteSMAD, to_elementtree, to_string, dump, validate

import sys
sys.path.insert(0, '../') # Adiciona a pasta pai no Path para ser usada na linha abaixo
from information_model import SwitchingCommand as swc

from rede.xml2objects import carregar_topologia

class SubscreverACom(FipaSubscribeProtocol):
    def __init__(self, agent: AgenteSMAD, message=None, is_initiator=True):
        super().__init__(agent, message=message, is_initiator=is_initiator)
        
    def handle_agree(self, message):
        display_message(self.agent.aid.name, 'Inscrito em ACom')

    def handle_inform(self, message: ACLMessage):    
        # TODO: Funções chamadas de acordo com a ontologia da mensagem
        def handle_outage(message):
            display_message(self.agent.aid.name, 'Mensagem INFORM recebida de %s' % message.sender.localname)
            print(message.content)

        # Chama a função que corresponde à ontologia da mensagem
        try:
            locals()[f'handle_{message.ontology}'](message)
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
        display_message(self.agent.aid.name, f'Conteúdo da mensagem: {message.content}')

    def handle_failure(self, message: ACLMessage):
        display_message(self.agent.aid.name, 'Falha em execução de comando')
        display_message(self.agent.aid.name, f'Conteúdo da mensagem: {message.content}')

    def handle_inform(self, message: ACLMessage):
        display_message(self.agent.aid.name, 'Chaveamento realizado')
        display_message(self.agent.aid.name, f'Conteúdo da mensagem: {message.content}')


class AgenteDC(AgenteSMAD):
    def __init__(self, aid, subestacao, debug=False):
        super().__init__(aid, subestacao, debug)
        self.behaviours.append(EnviarComando(self))
        display_message(self.aid.name, "Agente instanciado")

        #Inicio cod Tiago para o agente diagnostico
        self.subestacao = subestacao
        self.relatorios_restauracao = list()
        self.topologia_subestacao = carregar_topologia(subestacao)
        display_message(self.aid.name,"Subestacao {SE} carregada com sucesso".format(SE=subestacao))
        self.podas = list()
        self.podas_possiveis = list()
        self.setores_faltosos = list()
        #comportamento_requisicao = CompRequest1(self)
        #self.behaviours.append(comportamento_requisicao)
        #comp_contractnet_participante = CompContractNet1(self)
        #self.behaviours.append(comp_contractnet_participante)
        #Final cod Tiago para o agente diagnostico

    def enviar_comando_de_chave(self, switching_command: swc.SwitchingCommand, acom_aid: AID):
        # Valida objeto de informação
        validate(switching_command)
        # Monta envelope de mensagem ACL
        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.add_receiver(acom_aid)
        message.set_ontology('SwitchingCommand')
        message.set_content(to_elementtree(switching_command))
        def later():
            # Se o ACom já estiver na tabela
            if hasattr(self, 'agentInstance') and acom_aid.name in self.agentInstance.table:
                # Envia mensagem
                self.send(message)
            else:
                # Reenvia mensagem 5 segundos mais tarde
                self.call_later(5.0, later)
        later()


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

