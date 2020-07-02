import datetime
import time
from random import random
from uuid import uuid4

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import (FipaRequestProtocol,
                                       FipaSubscribeProtocol, TimedBehaviour)
from pade.misc.utility import display_message

from core.common import AgenteSMAD, to_elementtree, to_string, dump, validate
from core.ied import IED

import sys
sys.path.insert(0, '../')
from information_model import SwitchingCommand as swc
from information_model import OutageEvent as out

 
class EnvioDeDados(FipaSubscribeProtocol):
    """Permite o cadastro de assinantes (em especial, o ADC)
    para que recebam mensagens relativas
    à ocorrência de uma falta
    """

    def __init__(self, agent: AgenteSMAD):
        super().__init__(agent, is_initiator=False)

    def handle_subscribe(self, message: ACLMessage):
        self.register(message.sender)
        # Criar resposta de aceite
        reply = message.create_reply()
        reply.set_performative(ACLMessage.AGREE)
        self.agent.send(reply)

    def handle_not_understood(self, message):
        display_message(self.agent.aid.name, 'Mensagem incompreendida')


class ReceberComando(FipaRequestProtocol):
    """Recebe lista de comandos (do ADC)
    para manobra de chaves
    *SwitchingCommand*
    """
    obj = 'SwitchingCommand'

    def __init__(self, agent: AgenteSMAD):
        super().__init__(agent, is_initiator=False)

    def handle_request(self, message: ACLMessage):
        """Recepção de mensagem de comando 
        (conteúdo deve ser um SwitchingCommand)
        OBS: Mensagem recebida deve ser processada e respondida
        com agree / refuse / not_understood"""

        # Esperado SwitchingCommand
        if message.ontology != ReceberComando.obj:
            reply = message.create_reply()
            reply.set_performative(ACLMessage.NOT_UNDERSTOOD)
            reply.set_ontology('')
            reply.set_content(f'Unexpected ontology {message.ontology}')
            self.agent.send(reply)
            return

        # Lista que armazena ações requisitadas
        buffer_leitura_acoes = []
        # Lê documento recebido
        try:
            # Recupera instância SwitchingCommand ("cast" para dar uma dica pro Intellisense [Ctrl+Space])
            root: swc.SwitchingCommand = swc.parseString(to_string(message.content))
            # Iterar em lista de SwitchAction
            for switchAction in root.get_SwitchingPlan().get_SwitchAction():
                switchId = switchAction.get_OperatedSwitch().get_mRID()
                actionKind = switchAction.get_kind()
                sequenceNumber = switchAction.get_sequenceNumber()
                buffer_leitura_acoes.append((sequenceNumber, switchId, actionKind))
    
        except Exception as e:
            # Captura erro de má formatação do documento.
            # Devolve uma mensagem not_understood e finaliza
            reply = message.create_reply()
            reply.set_performative(ACLMessage.NOT_UNDERSTOOD)
            reply.set_ontology('')
            reply.set_content(str(e))
            self.agent.send(reply)
            return

        # Ordena por sequenceNumber
        buffer_leitura_acoes.sort(key=lambda item: item[0])

        # Realiza ações
        try:
            for sequenceNumber, switchId, actionKind in buffer_leitura_acoes:
                self.agent.comandar_chave(switchId, actionKind)
        except KeyError as e:
            # Retorna falha ao não encontrar switchId
            reply = message.create_reply()
            reply.set_performative(ACLMessage.FAILURE)
            reply.set_content(str(e))
            self.agent.send(reply)
            return
        except Exception as e:
            # Retorna falha genérica desconhecida
            reply = message.create_reply()
            reply.set_performative(ACLMessage.FAILURE)
            reply.set_content('Unknown issue')
            self.agent.send(reply)
            return

        # Retorna sucesso
        reply = message.create_reply()
        reply.set_performative(ACLMessage.INFORM)
        reply.set_ontology('')
        self.agent.send(reply)
        return   
        

class AgenteCom(AgenteSMAD):

    def __init__(self, aid: AID, substation: str, enderecos_IEDs={}, debug=False):
        super().__init__(aid, substation, debug)

        # Instancia IEDs
        self.IEDs = {}
        for (_id, ip) in enderecos_IEDs.items():
            self.IEDs[_id] = IED(_id, ip, call_on_event=self.receber_evento, initial_breaker_position='close')

        # Adiciona behaviours
        self.behaviours_enviodedados = EnvioDeDados(self) # Permite enviar dados ao ADC
        self.behaviours.append(self.behaviours_enviodedados) 
        self.behaviours_recebercomando = ReceberComando(self) # Permite receber comandos do ADC
        self.behaviours.append(self.behaviours_recebercomando)

        self.deadtime = 3.0 # Tempo em segundos do deadtime
        self.in_hold = False # Mantém o ACom à escuta durante um certo tempo de deadtime antes de notificar eventos
        self.document_to_send = None # Armazena temporariamente o documento enquanto ele está sendo construído


    def on_start(self):
        super().on_start()
        # Inicia conexão com todos os IEDs
        for ied, handle in self.IEDs.items():
            handle.connect()        

    def receber_evento(self, *args):
        """Função invocada quando ACom recebe mensagem do IED. Formato de entrada: \\
        ``args = (<IED instance>, 'PTOC', 'XCBR', 'BRKF')`` \\
        Mensagens dos recebidas pelo ACom são reunidas durante um ``deadtime``
        antes de serem todas encaminhadas (no formato adequado) ao ADC."""
        display_message(self.aid.name, f'Evento recebido do IED: {args[0].id} {args[1:]}')

        # Verifica se ACom já está à escuta de um conjunto de mensagens
        # (se já recebeu alguma mensagem durante o deadtime ou não)
        def send_document():
            # Sai do hold e envia documento
            self.in_hold = False
            # Cria pacote de mensagem e envia ao ADC
            message = ACLMessage(performative=ACLMessage.INFORM)
            message.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
            message.set_content(to_elementtree(self.document_to_send))
            self.behaviours_enviodedados.notify(message)

        if not self.in_hold:
            # Caso não esteja em deadtime, entra.
            self.in_hold = True
            # Cria novo documento
            outage = out.Outage()
            self.document_to_send = out.OutageEvent(Outage=outage)
            # Define o deadtime para enviar documento em 6 segundos
            self.call_later(self.deadtime, send_document)

        # Converte informações recebidas em formato CIM XML
        switchId = args[0].id
        switch = out.ProtectedSwitch(
            mRID=switchId, 
            normalOpen=False)
        for function in args[1:]:
            if function == 'XCBR':
                # Código do retorno
                value = out.Breaker_DiscreteValue_Integer('1')
                discrete_value = out.DiscreteValue(value=value)
                # Significado dos códigos
                value_to_alias_0 = out.ValueToAlias(
                    value=out.Breaker_DiscreteValue_Integer('0'), 
                    aliasName=out.Breaker_DiscreteMeasAlias.INVALID)
                value_to_alias_1 = out.ValueToAlias(
                    value=out.Breaker_DiscreteValue_Integer('1'), 
                    aliasName=out.Breaker_DiscreteMeasAlias.OPEN)
                value_to_alias_2 = out.ValueToAlias(
                    value=out.Breaker_DiscreteValue_Integer('2'), 
                    aliasName=out.Breaker_DiscreteMeasAlias.CLOSE)
                value_to_alias_3 = out.ValueToAlias(
                    value=out.Breaker_DiscreteValue_Integer('3'), 
                    aliasName=out.Breaker_DiscreteMeasAlias.INTERMEDIATE)
                value_alias_set = out.ValueAliasSet(Value=[value_to_alias_0, value_to_alias_1, value_to_alias_2, value_to_alias_3])
                # Insere na medição
                discrete = out.Discrete(
                    name=out.Discrete_Meas.BREAKER_POSITION, 
                    DiscreteValue=discrete_value,
                    ValueAliasSet=value_alias_set)
                switch.add_Discrete_Measurement(discrete)
            elif function in 'BRKF':
                # Código do retorno
                value = out.Breaker_DiscreteValue_Integer('1')
                discrete_value = out.DiscreteValue(value=value)
                # Significado dos códigos
                value_to_alias_0 = out.ValueToAlias(
                    value=out.Breaker_DiscreteValue_Integer('0'), 
                    aliasName=out.Breaker_DiscreteMeasAlias.FALSE)
                value_to_alias_1 = out.ValueToAlias(
                    value=out.Breaker_DiscreteValue_Integer('1'), 
                    aliasName=out.Breaker_DiscreteMeasAlias.TRUE)
                value_alias_set = out.ValueAliasSet(Value=[value_to_alias_0, value_to_alias_1])
                discrete = out.Discrete(
                    name=out.Discrete_Meas.BREAKER_FAILURE, 
                    DiscreteValue=discrete_value,
                    ValueAliasSet=value_alias_set)
                switch.add_Discrete_Measurement(discrete)

        # Adiciona Switch ao documento temporário
        self.document_to_send.get_Outage().add_ProtectedSwitch(switch)

    def comandar_chave(self, switchId=None, action='open'):
        """Chama a instância do IED para operar chave. 
        A ``id`` do switch coincide com a ``id`` do IED
        """
        self.IEDs[switchId].operate(action)
