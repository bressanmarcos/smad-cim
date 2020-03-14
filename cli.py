# from core.core import to_string, to_elementtree
from uuid import uuid4
import xml.etree.ElementTree as ET
import datetime
import time
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage

from core.adc import AgenteDC

a = AgenteDC(AID('agente_dc'), 'S1', debug=False)

b = a.behaviours[0]


print(b)

# def now():
#     # Calculate the offset taking into account daylight saving time
#     utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
#     utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
#     return datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset))


# outage = o.parseString("""
# <ns0:Outage xmlns:ns0="grei.ufc.br/smad" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
#   <ns0:mRID>790c15e2-d1a1-4faf-bcf6-3c7f947ecff4</ns0:mRID>
#   <ns0:startTime>2020-01-31T14:19:56.767846-03:00</ns0:startTime>
#   <ns0:title>Outage</ns0:title>
#   <ns0:cause>TimeOvercurrent</ns0:cause>
#   <ns0:OpenedSwitches>
#     <ns0:mRID>CH14</ns0:mRID>
#     <ns0:Measurements xsi:type="Discrete_Type">
#       <ns0:name>BreakerPosition</ns0:name>
#       <ns0:DiscreteValues>
#         <ns0:value>10</ns0:value>
#       </ns0:DiscreteValues>
#       <ns0:ValueAliasSet>
#         <ns0:Values>
#           <ns0:value>1</ns0:value>
#           <ns0:aliasName>True</ns0:aliasName>
#         </ns0:Values>
#         <ns0:Values>
#           <ns0:value>0</ns0:value>
#           <ns0:aliasName>False</ns0:aliasName>
#         </ns0:Values>
#       </ns0:ValueAliasSet>
#     </ns0:Measurements>
#     <ns0:Measurements xsi:type="Discrete_Type">
#       <ns0:name>BreakerFailure</ns0:name>
#       <ns0:DiscreteValues>
#         <ns0:value>1</ns0:value>
#       </ns0:DiscreteValues>
#       <ns0:ValueAliasSet>
#         <ns0:Values>
#           <ns0:value>1</ns0:value>
#           <ns0:aliasName>True</ns0:aliasName>
#         </ns0:Values>
#         <ns0:Values>
#           <ns0:value>0</ns0:value>
#           <ns0:aliasName>False</ns0:aliasName>
#         </ns0:Values>
#       </ns0:ValueAliasSet>
#     </ns0:Measurements>
#   </ns0:OpenedSwitches>
#   <ns0:OpenedSwitches>
#     <ns0:mRID>CH13</ns0:mRID>
#         <ns0:Measurements xsi:type="Discrete_Type">
#       <ns0:name>BreakerPosition</ns0:name>
#       <ns0:DiscreteValues>
#         <ns0:value>1</ns0:value>
#       </ns0:DiscreteValues>
#       <ns0:ValueAliasSet>
#         <ns0:Values>
#           <ns0:value>1</ns0:value>
#           <ns0:aliasName>True</ns0:aliasName>
#         </ns0:Values>
#         <ns0:Values>
#           <ns0:value>0</ns0:value>
#           <ns0:aliasName>False</ns0:aliasName>
#         </ns0:Values>
#       </ns0:ValueAliasSet>
#     </ns0:Measurements>
#   </ns0:OpenedSwitches>
# </ns0:Outage>
# """)
# print(outage.get_mRID())

# a = dict()

# if not a:
#     print('not a')


# tree: e_tree._Element
# tree = outage.to_etree()


# value = tree.xpath(
#     "i:OpenedSwitches/i:Discrete_Measurement[i:name='BreakerFailure']/i:DiscreteValues/i:value",
#     namespaces={'i': 'grei.ufc.br/smad'}
# )[0].text

# alias = tree.xpath(
#     "i:OpenedSwitches/i:Discrete_Measurement[i:name='BreakerFailure']/i:ValueAliasSet/i:Values[i:value='{}']/i:aliasName".format(
#         value),
#     namespaces={'i': 'grei.ufc.br/smad'}
# )[0].text

# print(alias)


# content = dict()
# content['dados'] = dict()
# content['dados']['BRKF'] = list()
# content['dados']['chaves'] = list()
# content['dados']['leitura_falta'] = [x.text for x in tree.findall(
#     "OpenedSwitches/mRID", namespaces={'': 'grei.ufc.br/smad'})]

# for chave in content['dados']['leitura_falta']:
#   breaker_position = tree.findall(
#         "OpenedSwitches[mRID='{}']/Measurements[name='BreakerPosition']/DiscreteValues/value".format(
#             chave),
#             namespaces={'': 'grei.ufc.br/smad'})[0].text

#   breaker_failure = tree.findall(
#         "OpenedSwitches[mRID='{}']/Measurements[name='BreakerFailure']/DiscreteValues/value".format(
#             chave),
#             namespaces={'': 'grei.ufc.br/smad'})
#   breaker_failure = len(breaker_failure) and breaker_failure[0].text is '1'

#   if breaker_position is '1':
#     content['dados']['chaves'].append(chave)
#   if breaker_failure:
#     content['dados']['BRKF'].append(chave)

# print(content)

