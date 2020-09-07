import os
os.sys.path.insert(0, os.getcwd())
from xml.etree import ElementTree as ET
from rede.network import *

def parse():
    TEXT = ''

    # Terminais criados com ConnectivityNode:  (
    # - Switch
    # - EnergyConsumer
    # - BusbarSecton
    # )

    # Terminais SEM CN: (
    # - ACLineSegment
    # - Transformador)

    dom = ET.parse('./rede/models/rede-rnp.xml')
    root = dom.getroot()
    
    # chaves
    for elem in root.findall('elementos/chave'):
        TEXT += f"""
    {elem.attrib['nome']} = Switch(IdentifiedObject_mRID='{elem.attrib['nome']}', Switch_normalOpen={elem.attrib['estado']=="aberto"}, Switch_open={elem.attrib['estado']=="aberto"})
    Terminal(Terminal_sequenceNumber=1, Terminal_ConductingEquipment={elem.attrib['nome']}, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='{elem.attrib['nome']}_1'))
    Terminal(Terminal_sequenceNumber=2, Terminal_ConductingEquipment={elem.attrib['nome']}, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='{elem.attrib['nome']}_2'))"""

    # nos
    for elem in root.findall('elementos/no'):
        nome = elem.attrib['nome']
        if nome not in ['S1','S2','S3']:
            ativa = elem.find('potencia[@tipo="ativa"]')
            reativa = elem.find('potencia[@tipo="reativa"]')
            TEXT += f"""
    {elem.attrib['nome']} = EnergyConsumer(
        IdentifiedObject_mRID='{elem.attrib['nome']}', 
        EnergyConsumer_p=ActivePower(UnitMultiplier('{ativa.attrib['multip']}'), UnitSymbol('{ativa.attrib['unid']}'), Decimal('{ativa.text.strip()}')), 
        EnergyConsumer_q=ReactivePower(UnitMultiplier('{ativa.attrib['multip']}'), UnitSymbol('{reativa.attrib['unid']}'), Decimal('{ativa.text.strip()}')))
    {elem.attrib['nome']}.ConductingEquipment_Terminals = [Terminal(Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='{elem.attrib['nome']}'))]"""

    # setor
    for elem in root.findall('elementos/setor'):
        TEXT += f"""
    setor_{elem.attrib['nome']} = TopologicalNode(IdentifiedObject_mRID='{elem.attrib['nome']}')"""

    # substaçao
    for elem in root.findall('elementos/subestacao'):
        # Substação
        TEXT += f"""
    subestacao_{elem.attrib['nome']} = Substation(IdentifiedObject_mRID='{elem.attrib['nome']}')"""
        # Barramento
        TEXT += f"""
    {elem.attrib['nome']} = BusbarSection(IdentifiedObject_mRID='{elem.attrib['nome']}', Equipment_EquipmentContainer=subestacao_{elem.attrib['nome']})"""

    # transformador
    for elem in root.findall('elementos/transformador'):
        potencia = elem.find('potencia')
        impedancia_seq_pos = elem.find('impedancia[@tipo="seq_pos"]')
        impedancia_seq_zero = elem.find('impedancia[@tipo="seq_zero"]')
        transformador = elem.attrib['nome']
        primario = elem.find('enrolamento[@tipo="primario"]')
        secundario = elem.find('enrolamento[@tipo="secundario"]')
        barramento = elem.attrib['nome'].split('_')[0]
        TEXT += f"""
    {transformador}_primario = PowerTransformerEnd(
        PowerTransformerEnd_ratedS=ApparentPower(ApparentPower_multiplier=UnitMultiplier('{potencia.attrib['multip']}'), ApparentPower_unit=UnitSymbol('{potencia.attrib['unid']}'), ApparentPower_value=Decimal('{potencia.text.strip()}')), 
        PowerTransformerEnd_endNumber=1, 
        PowerTransformerEnd_ratedU=Voltage(Voltage_multiplier=UnitMultiplier('{primario.find('tensao').attrib['multip']}'), Voltage_unit=UnitSymbol('{primario.find('tensao').attrib['unid']}'), Voltage_value=Decimal('{primario.find('tensao').text.strip()}')),
        PowerTransformerEnd_r=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('{impedancia_seq_pos.find('resistencia').text.strip() or Decimal('0')}')),
        PowerTransformerEnd_r0=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('{impedancia_seq_zero.find('resistencia').text.strip() or Decimal('0')}')),
        PowerTransformerEnd_x=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('{impedancia_seq_pos.find('reatancia').text.strip() or Decimal('0')}')),
        PowerTransformerEnd_x0=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('{impedancia_seq_zero.find('reatancia').text.strip() or Decimal('0')}')),
    )
    {transformador}_secundario = PowerTransformerEnd(
        PowerTransformerEnd_ratedS=ApparentPower(ApparentPower_multiplier=UnitMultiplier('{potencia.attrib['multip']}'), ApparentPower_unit=UnitSymbol('{potencia.attrib['unid']}'), ApparentPower_value=Decimal('{potencia.text.strip()}')), 
        PowerTransformerEnd_endNumber=2, 
        PowerTransformerEnd_ratedU=Voltage(Voltage_multiplier=UnitMultiplier('{primario.find('tensao').attrib['multip']}'), Voltage_unit=UnitSymbol('{secundario.find('tensao').attrib['unid']}'), Voltage_value=Decimal('{secundario.find('tensao').text.strip()}')),
        PowerTransformerEnd_r=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0')),
        PowerTransformerEnd_r0=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0')),
        PowerTransformerEnd_x=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0')),
        PowerTransformerEnd_x0=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0')),
    )
    {transformador} = PowerTransformer(IdentifiedObject_mRID='{elem.attrib['nome']}', PowerTransformer_PowerTransformerEnd=[{transformador}_primario, {transformador}_secundario])
    t1 = Terminal(Terminal_ConductingEquipment={transformador}, Terminal_sequenceNumber=1, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='{transformador}_1'))
    t2 = Terminal(Terminal_ConductingEquipment={transformador}, Terminal_sequenceNumber=2, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='{transformador}_2'))
    {barramento}.add_ConductingEquipment_Terminals(Terminal(Terminal_sequenceNumber=1+len({barramento}.ConductingEquipment_Terminals), Terminal_ConnectivityNode=t2.Terminal_ConnectivityNode))"""
    
    # alimentador
    for elem in root.findall('elementos/alimentador'):
        alimentador = elem.attrib['nome']
        barramento = elem.attrib['nome'].split('_')[0]
        TEXT += f"""
    {alimentador}_feeder = Feeder(IdentifiedObject_mRID='{alimentador}')
    {barramento}.add_ConductingEquipment_Terminals(Terminal(Terminal_sequenceNumber=1+len({barramento}.ConductingEquipment_Terminals), Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='{alimentador}')))"""

    # trecho
    for elem in root.findall('elementos/trecho'):
        comprimento = elem.find('comprimento')
        TEXT += f"""
    {elem.attrib['nome']} = ACLineSegment(IdentifiedObject_mRID='{elem.attrib['nome']}', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('{comprimento.attrib['multip']}'), UnitSymbol('{comprimento.attrib['unid']}'), Decimal('{comprimento.text.strip()}')))"""
    
    # per length
    for elem in root.findall('elementos/condutor'):
        nome_real = elem.attrib['nome']
        nome = elem.attrib['nome'].strip().replace('.', '').replace('/', '').replace(' ', '')
        TEXT += f"""
    {nome} = PerLengthSequenceImpedance(IdentifiedObject_mRID='{nome_real}', 
        PerLengthSequenceImpedance_r=ResistancePerLength(ResistancePerLength_multiplier=UnitMultiplier('none'), ResistancePerLength_unit=UnitSymbol('ohmPerm'), ResistancePerLength_value=Decimal('{elem.attrib['rp']}')),
        PerLengthSequenceImpedance_r0=ResistancePerLength(ResistancePerLength_multiplier=UnitMultiplier('none'), ResistancePerLength_unit=UnitSymbol('ohmPerm'), ResistancePerLength_value=Decimal('{elem.attrib['rz']}')),
        PerLengthSequenceImpedance_x=ReactancePerLength(ReactancePerLength_multiplier=UnitMultiplier('none'), ReactancePerLength_unit=UnitSymbol('ohmPerm'), ReactancePerLength_value=Decimal('{elem.attrib['xp']}')),
        PerLengthSequenceImpedance_x0=ReactancePerLength(ReactancePerLength_multiplier=UnitMultiplier('none'), ReactancePerLength_unit=UnitSymbol('ohmPerm'), ReactancePerLength_value=Decimal('{elem.attrib['xz']}'))
    )"""
        TEXT += f"""  
    {nome}_limit = OperationalLimitSet(IdentifiedObject_mRID='{nome_real}', OperationalLimitSet_OperationalLimitValue=[CurrentLimit(CurrentLimit_value=CurrentFlow(CurrentFlow_multiplier=UnitMultiplier('none'), CurrentFlow_unit=UnitSymbol('A'), CurrentFlow_value=Decimal('{elem.attrib['ampacidade']}')))])"""


    ################### Topologia
    S1_count = 0
    S2_count = 0
    S3_count = 0
    CH16_count = 0
    CH11_count = 0
    CH8_count = 0
    CH3_count = 0

    for elem in root.findall('topologia/elemento[@tipo="trecho"]'):
        n1 = elem.find('n1')
        n2 = elem.find('n2')

        for child in n1:
            elem_1 = child.attrib['nome']
            if elem_1 == 'S1':
                TEXT += f'''
    cn_eqs = [[eq.Terminal_ConductingEquipment for eq in tt.Terminal_ConnectivityNode.ConnectivityNode_Terminals] for tt in {elem_1}.ConductingEquipment_Terminals]
    idx = next(i for i in range(len(cn_eqs)) if len(cn_eqs[i]) == 1)'''
                TEXT += f'''
    cn_1 = {child.attrib['nome']}.ConductingEquipment_Terminals[idx].Terminal_ConnectivityNode'''
                S1_count += 1
            elif elem_1 == 'S2':
                TEXT += f'''
    cn_eqs = [[eq.Terminal_ConductingEquipment for eq in tt.Terminal_ConnectivityNode.ConnectivityNode_Terminals] for tt in {elem_1}.ConductingEquipment_Terminals]
    idx = next(i for i in range(len(cn_eqs)) if len(cn_eqs[i]) == 1)'''
                TEXT += f'''
    cn_1 = {child.attrib['nome']}.ConductingEquipment_Terminals[idx].Terminal_ConnectivityNode'''
                S2_count += 1
            elif elem_1 == 'S3':
                TEXT += f'''
    cn_eqs = [[eq.Terminal_ConductingEquipment for eq in tt.Terminal_ConnectivityNode.ConnectivityNode_Terminals] for tt in {elem_1}.ConductingEquipment_Terminals]
    idx = next(i for i in range(len(cn_eqs)) if len(cn_eqs[i]) == 1)'''
                TEXT += f'''
    cn_1 = {child.attrib['nome']}.ConductingEquipment_Terminals[idx].Terminal_ConnectivityNode'''
                S3_count += 1
            elif child.tag == 'no':
                TEXT += f'''
    cn_1 = {child.attrib['nome']}.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode'''
            elif elem_1 == 'CH16':
                TEXT += f'''
    cn_1 = {child.attrib['nome']}.ConductingEquipment_Terminals[{CH16_count}].Terminal_ConnectivityNode'''
                CH16_count += 1
            elif elem_1 == 'CH11':
                TEXT += f'''
    cn_1 = {child.attrib['nome']}.ConductingEquipment_Terminals[{CH11_count}].Terminal_ConnectivityNode'''
                CH11_count += 1
            elif elem_1 == 'CH8':
                TEXT += f'''
    cn_1 = {child.attrib['nome']}.ConductingEquipment_Terminals[{CH8_count}].Terminal_ConnectivityNode'''
                CH8_count += 1
            elif elem_1 == 'CH3':
                TEXT += f'''
    cn_1 = {child.attrib['nome']}.ConductingEquipment_Terminals[{CH3_count}].Terminal_ConnectivityNode'''
                CH3_count += 1
            elif child.tag == 'chave':
                TEXT += f'''
    cn_1 = {child.attrib['nome']}.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode'''
            else:
                raise Exception(f'que loco mano {child.tag}')

        for child in n2:
            elem_2 = child.attrib['nome']
            if elem_2 == 'S1':
                TEXT += f'''
    cn_eqs = [[eq.Terminal_ConductingEquipment for eq in tt.Terminal_ConnectivityNode.ConnectivityNode_Terminals] for tt in {elem_2}.ConductingEquipment_Terminals]
    idx = next(i for i in range(len(cn_eqs)) if len(cn_eqs[i]) == 1)'''
                TEXT += f'''
    cn_2 = {child.attrib['nome']}.ConductingEquipment_Terminals[idx].Terminal_ConnectivityNode'''
                S1_count += 1
            elif elem_2 == 'S2':
                TEXT += f'''
    cn_eqs = [[eq.Terminal_ConductingEquipment for eq in tt.Terminal_ConnectivityNode.ConnectivityNode_Terminals] for tt in {elem_2}.ConductingEquipment_Terminals]
    idx = next(i for i in range(len(cn_eqs)) if len(cn_eqs[i]) == 1)'''
                TEXT += f'''
    cn_2 = {child.attrib['nome']}.ConductingEquipment_Terminals[idx].Terminal_ConnectivityNode'''
                S2_count += 1
            elif elem_2 == 'S3':
                TEXT += f'''
    cn_eqs = [[eq.Terminal_ConductingEquipment for eq in tt.Terminal_ConnectivityNode.ConnectivityNode_Terminals] for tt in {elem_2}.ConductingEquipment_Terminals]
    idx = next(i for i in range(len(cn_eqs)) if len(cn_eqs[i]) == 1)'''
                TEXT += f'''
    cn_2 = {child.attrib['nome']}.ConductingEquipment_Terminals[idx].Terminal_ConnectivityNode'''
                S3_count += 1
            elif child.tag == 'no':
                TEXT += f'''
    cn_2 = {child.attrib['nome']}.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode'''
            elif elem_2 == 'CH16':
                TEXT += f'''
    cn_2 = {child.attrib['nome']}.ConductingEquipment_Terminals[{CH16_count}].Terminal_ConnectivityNode'''
                CH16_count += 1
            elif elem_2 == 'CH11':
                TEXT += f'''
    cn_2 = {child.attrib['nome']}.ConductingEquipment_Terminals[{CH11_count}].Terminal_ConnectivityNode'''
                CH11_count += 1
            elif elem_2 == 'CH8':
                TEXT += f'''
    cn_2 = {child.attrib['nome']}.ConductingEquipment_Terminals[{CH8_count}].Terminal_ConnectivityNode'''
                CH8_count += 1
            elif elem_2 == 'CH3':
                TEXT += f'''
    cn_2 = {child.attrib['nome']}.ConductingEquipment_Terminals[{CH3_count}].Terminal_ConnectivityNode'''
                CH3_count += 1
            elif child.tag == 'chave':
                TEXT += f'''
    cn_2 = {child.attrib['nome']}.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode'''
            else:
                raise Exception(f'que loco mano {child.tag}')

        trecho = elem.attrib['nome']
        TEXT += f'''
    {trecho}.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    {trecho}.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2'''
        
        condutor = elem.find('condutores/condutor').attrib['nome'].strip().replace('.', '').replace('/', '').replace(' ', '')
        TEXT += f'''
    {trecho}.Equipment_OperationalLimitSet = [{condutor}_limit]
    {trecho}.ACLineSegment_PerLengthImpedance = {condutor}'''


    for elem in root.findall('topologia/elemento[@tipo="alimentador"]'):
        nome = elem.attrib['nome']
        for child in elem.find('setores'):
            setor = child.attrib['nome']
            TEXT += f'''
    {nome}_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_{setor})'''
        
    for elem in root.findall('topologia/elemento[@tipo="setor"]'):
        nome = 'setor_' + elem.attrib['nome']
        for child in elem.find('nos'):
            no = child.attrib['nome']
            TEXT += f'''
    to_visit = [terminal.Terminal_ConnectivityNode for terminal in {no}.ConductingEquipment_Terminals] # cn to visit
    while len(to_visit):
        cn = to_visit.pop(0)
        {nome}.add_TopologicalNode_ConnectivityNodes(cn)
        for terminal in cn.ConnectivityNode_Terminals:
            equipment = terminal.Terminal_ConductingEquipment
            if isinstance(equipment, ACLineSegment):
                other_terminal = list(filter(lambda term: id(term) != id(terminal), equipment.ConductingEquipment_Terminals))[0]
                other_cn = other_terminal.Terminal_ConnectivityNode
                if other_cn not in {nome}.TopologicalNode_ConnectivityNodes:
                    to_visit.append(other_cn)'''
    
    for elem in root.findall('topologia/elemento[@tipo="subestacao"]'):
        subestacao = 'subestacao_' + elem.attrib['nome']
        for child in elem.find('alimentadores'):
            alimentador = child.attrib['nome'] + '_feeder'
            TEXT += f'''
    {subestacao}.add_Substation_SubstationFeeder({alimentador})'''
        for child in elem.find('transformadores'):
            transformador = child.attrib['nome']
            barramento = transformador.split('_')[0]
            TEXT += f'''
    {subestacao}.add_EquipmentContainer_Equipments({transformador})'''


    return TEXT

with open('./rede/conversion/generate_cimrdf_xml.py', 'w') as file:
    TEXT = ''
    TEXT += '''
import os
os.sys.path.insert(0, os.getcwd())
from xml.etree import ElementTree as ET
from rede.network import *

def net():'''
    TEXT += parse()
    TEXT += '''

    elements = list(filter(lambda elem: elem.__class__.__module__ == 'rede.network', locals().values()))
    doc = DocumentCIMRDF()
    doc.add_recursively(elements)
    doc.tofile('./rede/models/rede-cim.xml')
net()
'''
    file.write(TEXT)

