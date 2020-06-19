import datetime
import time
from random import random
from uuid import uuid4

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import (FipaRequestProtocol,
                                       FipaSubscribeProtocol, TimedBehaviour)
from pade.misc.utility import display_message

from common import AgenteSMAD, to_elementtree, to_string


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
    *SwitchingPlan*
    """

    def __init__(self, agent: AgenteSMAD):
        super().__init__(agent, is_initiator=False)

    def handle_request(self, message):
        """Recepção de mensagem de comando 
        (conteúdo deve ser um SwitchingPlan)
        """
        pass


class AgenteCom(AgenteSMAD):

    def __init__(self, aid: AID, substation: str, enderecos_IEDs={}, debug=False):
        super().__init__(aid, substation, debug)
        self.enderecos_IEDs = enderecos_IEDs
        self.behaviours.append(EnvioDeDados(self))
        self.behaviours.append(ReceberComando(self))
        # self.call_later(10, self.definir_mensagem)

    def comandar_chave(self, switchId=None, action='open'):
        """Implementa rotina low-level para use case Comandar chave
        Deve ser futuramente acoplado com a libiec61850 para controle de relés
        Atualmente é somente um stub para controle de uma ÚNICA chave
        """
        value_to_write = 1 if action == 'open' else 2
        endereco = self.enderecos_IEDs[switchId]
        display_message(
            self.aid.name, f'Comando "{value_to_write}" ({action}) --> {switchId} [{endereco}]')

    def definir_mensagem(self):
        # Diagnosticar falta::Informar atuação de chaves
        event_message = ACLMessage(ACLMessage.INFORM)
        event_message.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
        event_message.set_ontology('outage')
        event_message.set_datetime_now()

        obj = outage.Outage_Type(uuid4())
        switch = outage.ProtectedSwitch('switch' + str(uuid4()))
        analog = outage.Analog(name=outage.Analog_Meas.CURRENT_MAGNITUDE)
        analog.set_phases(outage.PhaseCode.A)
        analog.set_unitMultiplier(outage.UnitMultiplier.K)
        analog.set_unitSymbol(outage.UnitSymbol.A)
        analog_value = outage.AnalogValue(value=random())
        analog.set_AnalogValue(analog_value)
        switch.add_Analog_Measurement(analog)
        discrete = outage.Discrete(name=outage.Discrete_Meas.BREAKER_POSITION)
        discrete.add_DiscreteValue(outage.DiscreteValue(
            value=outage.Breaker_DiscreteValue_Integer(1)))
        value_alias_set = outage.ValueAliasSet()
        value_alias_set.add_Value(outage.ValueToAlias(
            value=0, aliasName=outage.Breaker_DiscreteMeasAlias.INTERMEDIATE))
        value_alias_set.add_Value(outage.ValueToAlias(
            value=1, aliasName=outage.Breaker_DiscreteMeasAlias.OPEN))
        value_alias_set.add_Value(outage.ValueToAlias(
            value=2, aliasName=outage.Breaker_DiscreteMeasAlias.CLOSE))
        value_alias_set.add_Value(outage.ValueToAlias(
            value=3, aliasName=outage.Breaker_DiscreteMeasAlias.INVALID))

        discrete.set_ValueAliasSet(value_alias_set)
        switch.add_Discrete_Measurement(value=discrete)
        obj.add_ProtectedSwitch(switch)
        event_message.set_content(obj)

        event_message.as_xml()

        self.envio_behaviour.notify(event_message)
        self.call_later(2, self.main)


if __name__ == "__main__":
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
    enderecos_S3 = {"CH17": "192.168.0.117",
                    "CH18": "192.168.0.118",
                    "CH16": "192.168.0.116"}
    acom = AgenteCom(AID('acom1@localhost:9000'), 'S1', enderecos_S1)
    acom.comandar_chave('CH13', 'close')
