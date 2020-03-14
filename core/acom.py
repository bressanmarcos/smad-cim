from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaRequestProtocol, TimedBehaviour, FipaSubscribeProtocol
from pade.misc.utility import display_message

from core.common import AgenteSMAD, to_elementtree, to_string

import information_model as im


from uuid import uuid4
import datetime
import time


def now():
    # Calculate the offset taking into account daylight saving time
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    return datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset))


class AquisicaoDeDados(TimedBehaviour):
    def __init__(self, agent, time):
        super(AquisicaoDeDados, self).__init__(agent, time)
        self.agent: AgenteCom
        self.sync = 0

    def ler_dados(self):
        inputs_dict = dict()
        with open(self.agent.data_sources) as data_source:
            sync = int(data_source.readline())
            if(self.sync <= sync):
                for line in data_source:
                    chave_evento = line.rstrip().split(',')
                    inputs_dict[chave_evento[0]] = chave_evento[1:]
                # self.sync = sync + 1
        return inputs_dict

    def criar_documento(self, inputs_dict):
        # Cria documento com base nas leituras
        document = im.Outage_Type(
            mRID=str(uuid4()),
            title='Outage',
            startTime=now(),
        )
        # Itera sobre cada chave com registro de evento
        for key, value in inputs_dict.items():
            chave = im.ProtectedSwitch(mRID=key)
            document.add_ProtectedSwitch(chave)
            # Captura informações de cada chave
            for info in value:
                if "PTOC" == info:
                    document.set_cause("TimeOvercurrent")
                elif "PIOC" == info:
                    document.set_cause("InstantaneousOvercurrent")
                elif "BRKF" == info:
                    chave.add_Discrete_Measurement(
                        im.Discrete(
                            name='BreakerFailure',
                            DiscreteValue=im.DiscreteValue(value=im.Breaker_DiscreteMeasValue('1')),
                            ValueAliasSet=im.ValueAliasSet([
                                im.ValueToAlias(value=im.Breaker_DiscreteMeasValue('1'), aliasName='True'),
                                im.ValueToAlias(value=im.Breaker_DiscreteMeasValue('0'), aliasName='False'),
                            ]),
                        ),
                    )
        return document

    def enviar_documento(self, document):
        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.set_ontology(document.get_title())
        message.set_content(to_elementtree(document, name_='Outage'))
        message.add_receiver(self.agent.adc_aid)
        self.agent.send(message)

    def on_time(self):
        super(AquisicaoDeDados, self).on_time()
        try:
            dados = self.ler_dados()
            if dados:
                documento = self.criar_documento(dados)
                self.enviar_documento(documento)
        except FileNotFoundError:
            pass


class EnvioDeDados(FipaRequestProtocol):
    def __init__(self, agent):
        super(EnvioDeDados, self).__init__(agent, is_initiator=True)

    def handle_inform(self, message):
        pass


class Assinatura(FipaSubscribeProtocol):
    def __init__(self, agent):
        super(Assinatura, self).__init__(agent, is_initiator=False)


class AgenteCom(AgenteSMAD):
    TEMPO_AQUISICAO = 3.0

    def __init__(self, aid, substation, data_source, adc_aid, debug=False):
        super(AgenteCom, self).__init__(aid, substation, debug)
        self.data_sources = data_source
        self.adc_aid = adc_aid
        self.behaviours = [
            AquisicaoDeDados(self, AgenteCom.TEMPO_AQUISICAO),
            EnvioDeDados(self),
        ]
