from pade.core.agent import AID
from pade.acl.messages import ACLMessage
from core.adc import RecepcaoDeDados
from core import *
from xml.etree import ElementTree as ET


acom = AgenteCom(AID('agente_com'), 'S1', 'config_TRIP_S1.txt', None)
d = acom.behaviours[0].ler_dados()
document = acom.behaviours[0].criar_documento(d)

message = ACLMessage()
message.content = ET.fromstring(to_string(document.to_etree(name_='Outage')))


print(ET.tostring(message.content))




content = dict()
content['dados'] = dict()
content['dados']['BRKF'] = list()
content['dados']['chaves'] = list()
content['dados']['leitura_falta'] = [x.text for x in message.content.findall(
    "n:ProtectedSwitch/n:mRID", namespaces={'n': 'grei.ufc.br/smad'})]
for chave in content['dados']['leitura_falta']:
    # Lê a posição da chave
    breaker_position = message.content.findall(
        "n:ProtectedSwitch[n:mRID='{}']/n:Discrete_Measurement[n:name='BreakerPosition']/n:DiscreteValue/n:value".format(
            chave),
        namespaces={'n': 'grei.ufc.br/smad'})
    if breaker_position and breaker_position[0].text is '1':
        content['dados']['chaves'].append(chave)
    # Verifica se houve falha
    breaker_failure = message.content.findall(
        "n:ProtectedSwitch[n:mRID='{}']/n:Discrete_Measurement[n:name='BreakerFailure']/n:DiscreteValue/n:value".format(
            chave),
        namespaces={'n': 'grei.ufc.br/smad'})
    breaker_failure = len(breaker_failure) and breaker_failure[0].text is '1'
    if breaker_failure:
        content['dados']['BRKF'].append(chave)

print(content)