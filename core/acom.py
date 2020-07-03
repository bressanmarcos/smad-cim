import datetime
import time
from random import random
from uuid import uuid4

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import (FipaRequestProtocol,
                                       FipaSubscribeProtocol, TimedBehaviour)
from pade.misc.utility import display_message

from core.common import AgenteSMAD, to_elementtree, to_string, dump
from core.ied import IED

import sys

sys.path.insert(0, '../')
from information_model import SwitchingCommand as swc


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
        self.IEDs = {}
        for (_id, ip) in enderecos_IEDs.items():
            self.IEDs[_id] = IED(_id, ip, call_on_event=self.receber_evento, initial_breaker_position='close')
        self.behaviours.append(EnvioDeDados(self))
        self.behaviours.append(ReceberComando(self))

    def on_start(self):
        super().on_start()
        # Inicia conexão com todos os IEDs
        for ied, handle in self.IEDs.items():
            handle.connect()

    def receber_evento(self, *args):
        """Função invocada quando ACom recebe mensagem do IED. Formato de entrada: \\
        ``args = ('PTOC', 'XCBR', BRKF')`` \\
        Mensagens dos recebidas pelo ACom são reunidas durante um ``deadtime``
        antes de serem todas encaminhadas (no formato adequado) ao ADC."""
        # TODO: Para UC de diagóstico de Chaves
        display_message(self.aid.name, f'Evento recebido: {args}')
        pass

    def comandar_chave(self, switchId=None, action='open'):
        """Chama a instância do IED para operar chave.
        A ``id`` do switch coincide com a ``id`` do IED
        """
        self.IEDs[switchId].operate(action)
