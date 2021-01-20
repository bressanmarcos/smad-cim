import datetime
import os
import time
from random import random
from uuid import uuid4
from typing import List

from information_model import OutageEvent as out
from information_model import SwitchingCommand as swc
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.highlevel import (FipaRequestProtocol,
                                       FipaSubscribeProtocol)
from pade.misc.utility import display_message

from core.common import AgenteSMAD, dump, to_elementtree, to_string, validate
from core.common.enums import *
from core.ied import FileIED, SimulatedIED, IED


class AgenteCom(AgenteSMAD):

    def __init__(self, aid: AID, substation: str, IEDs: List[IED], debug=False):
        super().__init__(aid, substation, debug)

        # Instance IEDs
        self.IEDs = {}
        for ied in IEDs:
            self.IEDs[ied.id] = ied
            ied.callback = self.receive_ied_event

        # Adiciona behaviours
        self.behaviours_enviodedados = \
            FipaSubscribeProtocol(self, is_initiator=False)
        # Permite enviar dados ao ADC
        self.behaviours_recebercomando = \
            FipaRequestProtocol(self, is_initiator=False)
        # Permite receber comandos do ADC

        self.behaviours_enviodedados.set_subscribe_handler(self.handle_subscribe)
        self.behaviours_recebercomando.set_request_handler(self.handle_request)

        self.deadtime = 3.0  # Tempo em segundos do deadtime
        # Mantém o ACom à escuta durante um certo tempo de deadtime antes de notificar eventos
        self.in_hold = False
        # Armazena temporariamente o documento enquanto ele está sendo construído
        self.document_to_send = None

    def on_start(self):
        super().on_start()
        # Inicia conexão com todos os IEDs
        for handler in self.IEDs.values():
            handler.connect()

    def handle_subscribe(self, message: ACLMessage):
        """Permite o cadastro de assinantes (em especial, o ADC)
        para que recebam mensagens relativas à ocorrência de uma falta"""
        display_message(self.aid.name, f"New subscriber: {message.sender.name}")
        self.behaviours_enviodedados.subscribe(message)
        # Criar resposta de aceite
        reply = message.create_reply()
        self.behaviours_enviodedados.send_agree(reply)

    def handle_request(self, message: ACLMessage):
        """Recepção de mensagem de comando
        (conteúdo deve ser um SwitchingCommand)
        OBS: Mensagem recebida deve ser processada e respondida
        com agree / refuse / not_understood"""

        # Esperado SwitchingCommand
        if message.ontology != swc.__name__:
            reply = message.create_reply()
            reply.set_ontology('')
            reply.set_content(
                f'{GeneralError.UnexpectedOntology.value}: {message.ontology}')
            self.behaviours_recebercomando.send_not_understood(reply)
            return

        # Lista que armazena ações requisitadas
        buffer_leitura_acoes = []
        # Lê documento recebido
        try:
            # Recupera instância SwitchingCommand ("cast" para dar uma dica pro Intellisense [Ctrl+Space])
            root: swc.SwitchingCommand = \
                swc.parseString(to_string(message.content))
            # Iterar em lista de SwitchAction
            for switchAction in root.get_SwitchingPlan().get_SwitchAction():
                switchId = switchAction.get_OperatedSwitch().get_mRID()
                actionKind = switchAction.get_kind()
                sequenceNumber = switchAction.get_sequenceNumber()
                buffer_leitura_acoes.append(
                    (sequenceNumber, switchId, actionKind))

        except Exception as e:
            # Captura erro de má formatação do documento.
            # Devolve uma mensagem not_understood e finaliza
            reply = message.create_reply()
            reply.set_content(f'{GeneralError.BadFormatting.value}: {e}')
            self.behaviours_recebercomando.send_not_understood(reply)
            return

        # Ordena por sequenceNumber
        buffer_leitura_acoes.sort(key=lambda item: item[0])

        # Realiza ações
        try:
            for sequenceNumber, switchId, actionKind in buffer_leitura_acoes:
                self.comandar_chave(switchId, actionKind)
            # Retorna sucesso
            reply = message.create_reply()
            reply.set_content(CommandResult.Success.value)
            self.behaviours_recebercomando.send_inform(reply)

        except SwitchAlreadyInPosition as e:
            # Retorna sucesso, mas nenhuma operação foi realizada
            reply = message.create_reply()
            reply.set_content(f'{CommandResult.AlreadyInPosition.value}: {e}')
            self.behaviours_recebercomando.send_inform(reply)

        except KeyError as e:
            # Retorna falha ao não encontrar switchId
            reply = message.create_reply()
            reply.set_content(f'{CommandResult.NotFound.value}: {e}')
            self.behaviours_recebercomando.send_failure(reply)

        except Exception as e:
            # Retorna falha genérica desconhecida
            reply = message.create_reply()
            reply.set_content(f'{CommandResult.Unknown.value}: {e}')
            self.behaviours_recebercomando.send_failure(reply)

    def receive_ied_event(self, switch, *args):
        """Função invocada quando ACom recebe mensagem do IED. Formato de entrada: \\
        ``switch = <IED instance>`` e ``args = ('PTOC', 'XCBR', 'BRKF')`` \\
        Mensagens dos recebidas pelo ACom são reunidas durante um ``deadtime``
        antes de serem todas encaminhadas (no formato adequado) ao ADC."""
        switchId = switch.id
        display_message(
            self.aid.name, 
            f'Evento recebido do IED: {switch.id} {args}'
        )

        # Verifica se ACom já está à escuta de um conjunto de mensagens
        # (se já recebeu alguma mensagem durante o deadtime ou não)
        def send_document():
            # Sai do hold e envia documento
            self.in_hold = False
            # Cria pacote de mensagem e envia ao ADC
            message = ACLMessage()
            message.set_ontology(out.__name__)
            message.set_content(to_elementtree(self.document_to_send))
            self.behaviours_enviodedados.send_inform(message)

        if not self.in_hold:
            # Caso não esteja em deadtime, entra.
            self.in_hold = True
            # Cria novo documento
            outage = out.Outage()
            self.document_to_send = out.OutageEvent(Outage=outage)
            # Define o deadtime para enviar documento em 6 segundos
            self.call_later(self.deadtime, send_document)

        # Converte informações recebidas em formato CIM XML
        switch = out.ProtectedSwitch(
            mRID=switchId,
            normalOpen=False)
        for function in args:
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
                value_alias_set = out.ValueAliasSet(
                    Value=[
                        value_to_alias_0, 
                        value_to_alias_1, 
                        value_to_alias_2, 
                        value_to_alias_3
                    ]
                )
                # Insere na medição
                discrete = out.Discrete(
                    name=out.Discrete_Meas.BREAKER_POSITION,
                    DiscreteValue=discrete_value,
                    ValueAliasSet=value_alias_set)
                switch.add_Discrete_Measurement(discrete)
            elif function == 'BRKF':
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
                value_alias_set = out.ValueAliasSet(
                    Value=[value_to_alias_0, value_to_alias_1])
                discrete = out.Discrete(
                    name=out.Discrete_Meas.BREAKER_FAILURE,
                    DiscreteValue=discrete_value,
                    ValueAliasSet=value_alias_set)
                switch.add_Discrete_Measurement(discrete)

        # Adiciona Switch ao documento temporário
        self.document_to_send.get_Outage().add_ProtectedSwitch(switch)

    def comandar_chave(self, switchId, action='open'):
        """Chama a instância do IED para operar chave.
        A ``id`` do switch coincide com a ``id`` do IED
        """
        breaker_position = self.IEDs[switchId].get_breaker_position()
        if action == breaker_position:
            raise SwitchAlreadyInPosition(
                f'Chave já está na posição solicitada ({action})')
        self.IEDs[switchId].operate(action)
