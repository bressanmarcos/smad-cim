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
from information_model import OutageEvent as out

from rede.rdf2mygrid import carregar_topologia

class SubscreverACom(FipaSubscribeProtocol):
    def __init__(self, agent: AgenteSMAD, message=None, is_initiator=True):
        super().__init__(agent, message=message, is_initiator=is_initiator)
        
    def handle_agree(self, message):
        display_message(self.agent.aid.name, 'Inscrito em ACom')

    def handle_inform(self, message: ACLMessage):    
        """Receve notificação de evento do ACom. \\
        ``message.content`` é recebida no formato OutageEvent
        """
        """Sequência de operações realizada:
            - 1) Análise de descoordenação
            -- a) Encontrar alimentador da chave (ver topologia carregada)
            -- b) 
        """
        lista_de_chaves = {}
        root: out.OutageEvent = out.parseString(to_string(message.content))
        for switch in root.get_Outage().get_ProtectedSwitch():
            switch: out.ProtectedSwitch
            switchId = switch.get_mRID()

            lista_de_chaves[switchId] = []

            for discrete_meas in switch.get_Discrete_Measurement():
                discrete_meas: out.Discrete
                discrete_meas_name = discrete_meas.get_name()
                discrete_meas_value = discrete_meas.get_DiscreteValue().get_value().get_valueOf_()
                if discrete_meas_name == out.Discrete_Meas.BREAKER_POSITION:
                    if discrete_meas_value == '1':
                        lista_de_chaves[switchId].append('breaker_position_open')
                elif discrete_meas_name == out.Discrete_Meas.BREAKER_FAILURE:
                    if discrete_meas_value == '1':
                        lista_de_chaves[switchId].append('breaker_failure')

        print(lista_de_chaves)

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
        self.topologia_subestacao = carregar_topologia('./rede/rede-cim.xml', subestacao)

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
        """Envia um objeto de informação do tipo SwitchingCommand ao ACom fornecido"""
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

