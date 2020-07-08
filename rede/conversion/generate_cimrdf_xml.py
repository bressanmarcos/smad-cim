
import os
os.sys.path.insert(0, os.getcwd())
from xml.etree import ElementTree as ET
from rede.network import *

def net():
    CH18 = Switch(IdentifiedObject_mRID='CH18', Switch_normalOpen=False, Switch_open=False)
    Terminal(Terminal_sequenceNumber=1, Terminal_ConductingEquipment=CH18, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH18_1'))
    Terminal(Terminal_sequenceNumber=2, Terminal_ConductingEquipment=CH18, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH18_2'))
    CH17 = Switch(IdentifiedObject_mRID='CH17', Switch_normalOpen=False, Switch_open=False)
    Terminal(Terminal_sequenceNumber=1, Terminal_ConductingEquipment=CH17, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH17_1'))
    Terminal(Terminal_sequenceNumber=2, Terminal_ConductingEquipment=CH17, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH17_2'))
    CH16 = Switch(IdentifiedObject_mRID='CH16', Switch_normalOpen=True, Switch_open=True)
    Terminal(Terminal_sequenceNumber=1, Terminal_ConductingEquipment=CH16, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH16_1'))
    Terminal(Terminal_sequenceNumber=2, Terminal_ConductingEquipment=CH16, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH16_2'))
    CH12 = Switch(IdentifiedObject_mRID='CH12', Switch_normalOpen=False, Switch_open=False)
    Terminal(Terminal_sequenceNumber=1, Terminal_ConductingEquipment=CH12, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH12_1'))
    Terminal(Terminal_sequenceNumber=2, Terminal_ConductingEquipment=CH12, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH12_2'))
    CH4 = Switch(IdentifiedObject_mRID='CH4', Switch_normalOpen=False, Switch_open=False)
    Terminal(Terminal_sequenceNumber=1, Terminal_ConductingEquipment=CH4, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH4_1'))
    Terminal(Terminal_sequenceNumber=2, Terminal_ConductingEquipment=CH4, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH4_2'))
    CH5 = Switch(IdentifiedObject_mRID='CH5', Switch_normalOpen=False, Switch_open=False)
    Terminal(Terminal_sequenceNumber=1, Terminal_ConductingEquipment=CH5, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH5_1'))
    Terminal(Terminal_sequenceNumber=2, Terminal_ConductingEquipment=CH5, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH5_2'))
    CH15 = Switch(IdentifiedObject_mRID='CH15', Switch_normalOpen=False, Switch_open=False)
    Terminal(Terminal_sequenceNumber=1, Terminal_ConductingEquipment=CH15, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH15_1'))
    Terminal(Terminal_sequenceNumber=2, Terminal_ConductingEquipment=CH15, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH15_2'))
    CH11 = Switch(IdentifiedObject_mRID='CH11', Switch_normalOpen=True, Switch_open=True)
    Terminal(Terminal_sequenceNumber=1, Terminal_ConductingEquipment=CH11, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH11_1'))
    Terminal(Terminal_sequenceNumber=2, Terminal_ConductingEquipment=CH11, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH11_2'))
    CH8 = Switch(IdentifiedObject_mRID='CH8', Switch_normalOpen=True, Switch_open=True)
    Terminal(Terminal_sequenceNumber=1, Terminal_ConductingEquipment=CH8, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH8_1'))
    Terminal(Terminal_sequenceNumber=2, Terminal_ConductingEquipment=CH8, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH8_2'))
    CH3 = Switch(IdentifiedObject_mRID='CH3', Switch_normalOpen=True, Switch_open=True)
    Terminal(Terminal_sequenceNumber=1, Terminal_ConductingEquipment=CH3, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH3_1'))
    Terminal(Terminal_sequenceNumber=2, Terminal_ConductingEquipment=CH3, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH3_2'))
    CH14 = Switch(IdentifiedObject_mRID='CH14', Switch_normalOpen=False, Switch_open=False)
    Terminal(Terminal_sequenceNumber=1, Terminal_ConductingEquipment=CH14, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH14_1'))
    Terminal(Terminal_sequenceNumber=2, Terminal_ConductingEquipment=CH14, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH14_2'))
    CH10 = Switch(IdentifiedObject_mRID='CH10', Switch_normalOpen=False, Switch_open=False)
    Terminal(Terminal_sequenceNumber=1, Terminal_ConductingEquipment=CH10, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH10_1'))
    Terminal(Terminal_sequenceNumber=2, Terminal_ConductingEquipment=CH10, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH10_2'))
    CH7 = Switch(IdentifiedObject_mRID='CH7', Switch_normalOpen=False, Switch_open=False)
    Terminal(Terminal_sequenceNumber=1, Terminal_ConductingEquipment=CH7, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH7_1'))
    Terminal(Terminal_sequenceNumber=2, Terminal_ConductingEquipment=CH7, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH7_2'))
    CH2 = Switch(IdentifiedObject_mRID='CH2', Switch_normalOpen=False, Switch_open=False)
    Terminal(Terminal_sequenceNumber=1, Terminal_ConductingEquipment=CH2, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH2_1'))
    Terminal(Terminal_sequenceNumber=2, Terminal_ConductingEquipment=CH2, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH2_2'))
    CH13 = Switch(IdentifiedObject_mRID='CH13', Switch_normalOpen=False, Switch_open=False)
    Terminal(Terminal_sequenceNumber=1, Terminal_ConductingEquipment=CH13, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH13_1'))
    Terminal(Terminal_sequenceNumber=2, Terminal_ConductingEquipment=CH13, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH13_2'))
    CH9 = Switch(IdentifiedObject_mRID='CH9', Switch_normalOpen=False, Switch_open=False)
    Terminal(Terminal_sequenceNumber=1, Terminal_ConductingEquipment=CH9, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH9_1'))
    Terminal(Terminal_sequenceNumber=2, Terminal_ConductingEquipment=CH9, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH9_2'))
    CH6 = Switch(IdentifiedObject_mRID='CH6', Switch_normalOpen=False, Switch_open=False)
    Terminal(Terminal_sequenceNumber=1, Terminal_ConductingEquipment=CH6, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH6_1'))
    Terminal(Terminal_sequenceNumber=2, Terminal_ConductingEquipment=CH6, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH6_2'))
    CH1 = Switch(IdentifiedObject_mRID='CH1', Switch_normalOpen=False, Switch_open=False)
    Terminal(Terminal_sequenceNumber=1, Terminal_ConductingEquipment=CH1, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH1_1'))
    Terminal(Terminal_sequenceNumber=2, Terminal_ConductingEquipment=CH1, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='CH1_2'))
    N1 = EnergyConsumer(
        IdentifiedObject_mRID='N1', 
        EnergyConsumer_p=ActivePower(UnitMultiplier('k'), UnitSymbol('W'), Decimal('5409.586')), 
        EnergyConsumer_q=ReactivePower(UnitMultiplier('k'), UnitSymbol('VAr'), Decimal('5409.586')))
    N1.ConductingEquipment_Terminals = [Terminal(Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='N1'))]
    M1 = EnergyConsumer(
        IdentifiedObject_mRID='M1', 
        EnergyConsumer_p=ActivePower(UnitMultiplier('k'), UnitSymbol('W'), Decimal('1957.12')), 
        EnergyConsumer_q=ReactivePower(UnitMultiplier('k'), UnitSymbol('VAr'), Decimal('1957.12')))
    M1.ConductingEquipment_Terminals = [Terminal(Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='M1'))]
    L1 = EnergyConsumer(
        IdentifiedObject_mRID='L1', 
        EnergyConsumer_p=ActivePower(UnitMultiplier('k'), UnitSymbol('W'), Decimal('1693.239')), 
        EnergyConsumer_q=ReactivePower(UnitMultiplier('k'), UnitSymbol('VAr'), Decimal('1693.239')))
    L1.ConductingEquipment_Terminals = [Terminal(Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='L1'))]
    D1 = EnergyConsumer(
        IdentifiedObject_mRID='D1', 
        EnergyConsumer_p=ActivePower(UnitMultiplier('k'), UnitSymbol('W'), Decimal('2308.962')), 
        EnergyConsumer_q=ReactivePower(UnitMultiplier('k'), UnitSymbol('VAr'), Decimal('2308.962')))
    D1.ConductingEquipment_Terminals = [Terminal(Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='D1'))]
    K1 = EnergyConsumer(
        IdentifiedObject_mRID='K1', 
        EnergyConsumer_p=ActivePower(UnitMultiplier('k'), UnitSymbol('W'), Decimal('3408.46')), 
        EnergyConsumer_q=ReactivePower(UnitMultiplier('k'), UnitSymbol('VAr'), Decimal('3408.46')))
    K1.ConductingEquipment_Terminals = [Terminal(Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='K1'))]
    K2 = EnergyConsumer(
        IdentifiedObject_mRID='K2', 
        EnergyConsumer_p=ActivePower(UnitMultiplier('k'), UnitSymbol('W'), Decimal('0')), 
        EnergyConsumer_q=ReactivePower(UnitMultiplier('k'), UnitSymbol('VAr'), Decimal('0')))
    K2.ConductingEquipment_Terminals = [Terminal(Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='K2'))]
    C1 = EnergyConsumer(
        IdentifiedObject_mRID='C1', 
        EnergyConsumer_p=ActivePower(UnitMultiplier('k'), UnitSymbol('W'), Decimal('1649.25')), 
        EnergyConsumer_q=ReactivePower(UnitMultiplier('k'), UnitSymbol('VAr'), Decimal('1649.25')))
    C1.ConductingEquipment_Terminals = [Terminal(Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='C1'))]
    J1 = EnergyConsumer(
        IdentifiedObject_mRID='J1', 
        EnergyConsumer_p=ActivePower(UnitMultiplier('k'), UnitSymbol('W'), Decimal('923.58')), 
        EnergyConsumer_q=ReactivePower(UnitMultiplier('k'), UnitSymbol('VAr'), Decimal('923.58')))
    J1.ConductingEquipment_Terminals = [Terminal(Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='J1'))]
    H1 = EnergyConsumer(
        IdentifiedObject_mRID='H1', 
        EnergyConsumer_p=ActivePower(UnitMultiplier('k'), UnitSymbol('W'), Decimal('1363.38')), 
        EnergyConsumer_q=ReactivePower(UnitMultiplier('k'), UnitSymbol('VAr'), Decimal('1363.38')))
    H1.ConductingEquipment_Terminals = [Terminal(Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='H1'))]
    F1 = EnergyConsumer(
        IdentifiedObject_mRID='F1', 
        EnergyConsumer_p=ActivePower(UnitMultiplier('k'), UnitSymbol('W'), Decimal('2330.95')), 
        EnergyConsumer_q=ReactivePower(UnitMultiplier('k'), UnitSymbol('VAr'), Decimal('2330.95')))
    F1.ConductingEquipment_Terminals = [Terminal(Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='F1'))]
    B1 = EnergyConsumer(
        IdentifiedObject_mRID='B1', 
        EnergyConsumer_p=ActivePower(UnitMultiplier('k'), UnitSymbol('W'), Decimal('1253.436')), 
        EnergyConsumer_q=ReactivePower(UnitMultiplier('k'), UnitSymbol('VAr'), Decimal('1253.436')))
    B1.ConductingEquipment_Terminals = [Terminal(Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='B1'))]
    I1 = EnergyConsumer(
        IdentifiedObject_mRID='I1', 
        EnergyConsumer_p=ActivePower(UnitMultiplier('k'), UnitSymbol('W'), Decimal('2770.75')), 
        EnergyConsumer_q=ReactivePower(UnitMultiplier('k'), UnitSymbol('VAr'), Decimal('2770.75')))
    I1.ConductingEquipment_Terminals = [Terminal(Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='I1'))]
    G1 = EnergyConsumer(
        IdentifiedObject_mRID='G1', 
        EnergyConsumer_p=ActivePower(UnitMultiplier('k'), UnitSymbol('W'), Decimal('1825.17')), 
        EnergyConsumer_q=ReactivePower(UnitMultiplier('k'), UnitSymbol('VAr'), Decimal('1825.17')))
    G1.ConductingEquipment_Terminals = [Terminal(Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='G1'))]
    E1 = EnergyConsumer(
        IdentifiedObject_mRID='E1', 
        EnergyConsumer_p=ActivePower(UnitMultiplier('k'), UnitSymbol('W'), Decimal('461.792')), 
        EnergyConsumer_q=ReactivePower(UnitMultiplier('k'), UnitSymbol('VAr'), Decimal('461.792')))
    E1.ConductingEquipment_Terminals = [Terminal(Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='E1'))]
    A1 = EnergyConsumer(
        IdentifiedObject_mRID='A1', 
        EnergyConsumer_p=ActivePower(UnitMultiplier('k'), UnitSymbol('W'), Decimal('506')), 
        EnergyConsumer_q=ReactivePower(UnitMultiplier('k'), UnitSymbol('VAr'), Decimal('506')))
    A1.ConductingEquipment_Terminals = [Terminal(Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='A1'))]
    setor_S3 = TopologicalNode(IdentifiedObject_mRID='S3')
    setor_K = TopologicalNode(IdentifiedObject_mRID='K')
    setor_H = TopologicalNode(IdentifiedObject_mRID='H')
    setor_C = TopologicalNode(IdentifiedObject_mRID='C')
    setor_L = TopologicalNode(IdentifiedObject_mRID='L')
    setor_J = TopologicalNode(IdentifiedObject_mRID='J')
    setor_M = TopologicalNode(IdentifiedObject_mRID='M')
    setor_D = TopologicalNode(IdentifiedObject_mRID='D')
    setor_N = TopologicalNode(IdentifiedObject_mRID='N')
    setor_F = TopologicalNode(IdentifiedObject_mRID='F')
    setor_B = TopologicalNode(IdentifiedObject_mRID='B')
    setor_I = TopologicalNode(IdentifiedObject_mRID='I')
    setor_G = TopologicalNode(IdentifiedObject_mRID='G')
    setor_E = TopologicalNode(IdentifiedObject_mRID='E')
    setor_A = TopologicalNode(IdentifiedObject_mRID='A')
    setor_S2 = TopologicalNode(IdentifiedObject_mRID='S2')
    setor_S1 = TopologicalNode(IdentifiedObject_mRID='S1')
    subestacao_S3 = Substation(IdentifiedObject_mRID='S3')
    S3 = BusbarSection(IdentifiedObject_mRID='S3', Equipment_EquipmentContainer=subestacao_S3)
    subestacao_S2 = Substation(IdentifiedObject_mRID='S2')
    S2 = BusbarSection(IdentifiedObject_mRID='S2', Equipment_EquipmentContainer=subestacao_S2)
    subestacao_S1 = Substation(IdentifiedObject_mRID='S1')
    S1 = BusbarSection(IdentifiedObject_mRID='S1', Equipment_EquipmentContainer=subestacao_S1)
    S3_T1_primario = PowerTransformerEnd(
        PowerTransformerEnd_ratedS=ApparentPower(ApparentPower_multiplier=UnitMultiplier('M'), ApparentPower_unit=UnitSymbol('VA'), ApparentPower_value=Decimal('15')), 
        PowerTransformerEnd_endNumber=1, 
        PowerTransformerEnd_ratedU=Voltage(Voltage_multiplier=UnitMultiplier('k'), Voltage_unit=UnitSymbol('V'), Voltage_value=Decimal('69')),
        PowerTransformerEnd_r=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0.868')),
        PowerTransformerEnd_r0=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0')),
        PowerTransformerEnd_x=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0.868')),
        PowerTransformerEnd_x0=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0')),
    )
    S3_T1_secundario = PowerTransformerEnd(
        PowerTransformerEnd_ratedS=ApparentPower(ApparentPower_multiplier=UnitMultiplier('M'), ApparentPower_unit=UnitSymbol('VA'), ApparentPower_value=Decimal('15')), 
        PowerTransformerEnd_endNumber=2, 
        PowerTransformerEnd_ratedU=Voltage(Voltage_multiplier=UnitMultiplier('k'), Voltage_unit=UnitSymbol('V'), Voltage_value=Decimal('13.8')),
        PowerTransformerEnd_r=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0')),
        PowerTransformerEnd_r0=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0')),
        PowerTransformerEnd_x=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0')),
        PowerTransformerEnd_x0=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0')),
    )
    S3_T1 = PowerTransformer(IdentifiedObject_mRID='S3_T1', PowerTransformer_PowerTransformerEnd=[S3_T1_primario, S3_T1_secundario])
    t1 = Terminal(Terminal_ConductingEquipment=S3_T1, Terminal_sequenceNumber=1, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='S3_T1_1'))
    t2 = Terminal(Terminal_ConductingEquipment=S3_T1, Terminal_sequenceNumber=2, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='S3_T1_2'))
    S3.add_ConductingEquipment_Terminals(Terminal(Terminal_sequenceNumber=1+len(S3.ConductingEquipment_Terminals), Terminal_ConnectivityNode=t2.Terminal_ConnectivityNode))
    S3_T2_primario = PowerTransformerEnd(
        PowerTransformerEnd_ratedS=ApparentPower(ApparentPower_multiplier=UnitMultiplier('M'), ApparentPower_unit=UnitSymbol('VA'), ApparentPower_value=Decimal('15')), 
        PowerTransformerEnd_endNumber=1, 
        PowerTransformerEnd_ratedU=Voltage(Voltage_multiplier=UnitMultiplier('k'), Voltage_unit=UnitSymbol('V'), Voltage_value=Decimal('69')),
        PowerTransformerEnd_r=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0.868')),
        PowerTransformerEnd_r0=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0')),
        PowerTransformerEnd_x=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0.868')),
        PowerTransformerEnd_x0=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0')),
    )
    S3_T2_secundario = PowerTransformerEnd(
        PowerTransformerEnd_ratedS=ApparentPower(ApparentPower_multiplier=UnitMultiplier('M'), ApparentPower_unit=UnitSymbol('VA'), ApparentPower_value=Decimal('15')), 
        PowerTransformerEnd_endNumber=2, 
        PowerTransformerEnd_ratedU=Voltage(Voltage_multiplier=UnitMultiplier('k'), Voltage_unit=UnitSymbol('V'), Voltage_value=Decimal('13.8')),
        PowerTransformerEnd_r=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0')),
        PowerTransformerEnd_r0=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0')),
        PowerTransformerEnd_x=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0')),
        PowerTransformerEnd_x0=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0')),
    )
    S3_T2 = PowerTransformer(IdentifiedObject_mRID='S3_T2', PowerTransformer_PowerTransformerEnd=[S3_T2_primario, S3_T2_secundario])
    t1 = Terminal(Terminal_ConductingEquipment=S3_T2, Terminal_sequenceNumber=1, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='S3_T2_1'))
    t2 = Terminal(Terminal_ConductingEquipment=S3_T2, Terminal_sequenceNumber=2, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='S3_T2_2'))
    S3.add_ConductingEquipment_Terminals(Terminal(Terminal_sequenceNumber=1+len(S3.ConductingEquipment_Terminals), Terminal_ConnectivityNode=t2.Terminal_ConnectivityNode))
    S2_T1_primario = PowerTransformerEnd(
        PowerTransformerEnd_ratedS=ApparentPower(ApparentPower_multiplier=UnitMultiplier('M'), ApparentPower_unit=UnitSymbol('VA'), ApparentPower_value=Decimal('15')), 
        PowerTransformerEnd_endNumber=1, 
        PowerTransformerEnd_ratedU=Voltage(Voltage_multiplier=UnitMultiplier('k'), Voltage_unit=UnitSymbol('V'), Voltage_value=Decimal('69')),
        PowerTransformerEnd_r=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0.868')),
        PowerTransformerEnd_r0=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0')),
        PowerTransformerEnd_x=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0.868')),
        PowerTransformerEnd_x0=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0')),
    )
    S2_T1_secundario = PowerTransformerEnd(
        PowerTransformerEnd_ratedS=ApparentPower(ApparentPower_multiplier=UnitMultiplier('M'), ApparentPower_unit=UnitSymbol('VA'), ApparentPower_value=Decimal('15')), 
        PowerTransformerEnd_endNumber=2, 
        PowerTransformerEnd_ratedU=Voltage(Voltage_multiplier=UnitMultiplier('k'), Voltage_unit=UnitSymbol('V'), Voltage_value=Decimal('13.8')),
        PowerTransformerEnd_r=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0')),
        PowerTransformerEnd_r0=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0')),
        PowerTransformerEnd_x=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0')),
        PowerTransformerEnd_x0=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0')),
    )
    S2_T1 = PowerTransformer(IdentifiedObject_mRID='S2_T1', PowerTransformer_PowerTransformerEnd=[S2_T1_primario, S2_T1_secundario])
    t1 = Terminal(Terminal_ConductingEquipment=S2_T1, Terminal_sequenceNumber=1, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='S2_T1_1'))
    t2 = Terminal(Terminal_ConductingEquipment=S2_T1, Terminal_sequenceNumber=2, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='S2_T1_2'))
    S2.add_ConductingEquipment_Terminals(Terminal(Terminal_sequenceNumber=1+len(S2.ConductingEquipment_Terminals), Terminal_ConnectivityNode=t2.Terminal_ConnectivityNode))
    S1_T1_primario = PowerTransformerEnd(
        PowerTransformerEnd_ratedS=ApparentPower(ApparentPower_multiplier=UnitMultiplier('M'), ApparentPower_unit=UnitSymbol('VA'), ApparentPower_value=Decimal('15')), 
        PowerTransformerEnd_endNumber=1, 
        PowerTransformerEnd_ratedU=Voltage(Voltage_multiplier=UnitMultiplier('k'), Voltage_unit=UnitSymbol('V'), Voltage_value=Decimal('69')),
        PowerTransformerEnd_r=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0.868')),
        PowerTransformerEnd_r0=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0')),
        PowerTransformerEnd_x=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0.868')),
        PowerTransformerEnd_x0=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0')),
    )
    S1_T1_secundario = PowerTransformerEnd(
        PowerTransformerEnd_ratedS=ApparentPower(ApparentPower_multiplier=UnitMultiplier('M'), ApparentPower_unit=UnitSymbol('VA'), ApparentPower_value=Decimal('15')), 
        PowerTransformerEnd_endNumber=2, 
        PowerTransformerEnd_ratedU=Voltage(Voltage_multiplier=UnitMultiplier('k'), Voltage_unit=UnitSymbol('V'), Voltage_value=Decimal('13.8')),
        PowerTransformerEnd_r=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0')),
        PowerTransformerEnd_r0=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0')),
        PowerTransformerEnd_x=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0')),
        PowerTransformerEnd_x0=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0')),
    )
    S1_T1 = PowerTransformer(IdentifiedObject_mRID='S1_T1', PowerTransformer_PowerTransformerEnd=[S1_T1_primario, S1_T1_secundario])
    t1 = Terminal(Terminal_ConductingEquipment=S1_T1, Terminal_sequenceNumber=1, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='S1_T1_1'))
    t2 = Terminal(Terminal_ConductingEquipment=S1_T1, Terminal_sequenceNumber=2, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='S1_T1_2'))
    S1.add_ConductingEquipment_Terminals(Terminal(Terminal_sequenceNumber=1+len(S1.ConductingEquipment_Terminals), Terminal_ConnectivityNode=t2.Terminal_ConnectivityNode))
    S1_T2_primario = PowerTransformerEnd(
        PowerTransformerEnd_ratedS=ApparentPower(ApparentPower_multiplier=UnitMultiplier('M'), ApparentPower_unit=UnitSymbol('VA'), ApparentPower_value=Decimal('15')), 
        PowerTransformerEnd_endNumber=1, 
        PowerTransformerEnd_ratedU=Voltage(Voltage_multiplier=UnitMultiplier('k'), Voltage_unit=UnitSymbol('V'), Voltage_value=Decimal('69')),
        PowerTransformerEnd_r=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0.868')),
        PowerTransformerEnd_r0=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0')),
        PowerTransformerEnd_x=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0.868')),
        PowerTransformerEnd_x0=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0')),
    )
    S1_T2_secundario = PowerTransformerEnd(
        PowerTransformerEnd_ratedS=ApparentPower(ApparentPower_multiplier=UnitMultiplier('M'), ApparentPower_unit=UnitSymbol('VA'), ApparentPower_value=Decimal('15')), 
        PowerTransformerEnd_endNumber=2, 
        PowerTransformerEnd_ratedU=Voltage(Voltage_multiplier=UnitMultiplier('k'), Voltage_unit=UnitSymbol('V'), Voltage_value=Decimal('13.8')),
        PowerTransformerEnd_r=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0')),
        PowerTransformerEnd_r0=Resistance(Resistance_multiplier=UnitMultiplier('none'), Resistance_unit=UnitSymbol('ohm'), Resistance_value=Decimal('0')),
        PowerTransformerEnd_x=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0')),
        PowerTransformerEnd_x0=Reactance(Reactance_multiplier=UnitMultiplier('none'), Reactance_unit=UnitSymbol('ohm'), Reactance_value=Decimal('0')),
    )
    S1_T2 = PowerTransformer(IdentifiedObject_mRID='S1_T2', PowerTransformer_PowerTransformerEnd=[S1_T2_primario, S1_T2_secundario])
    t1 = Terminal(Terminal_ConductingEquipment=S1_T2, Terminal_sequenceNumber=1, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='S1_T2_1'))
    t2 = Terminal(Terminal_ConductingEquipment=S1_T2, Terminal_sequenceNumber=2, Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='S1_T2_2'))
    S1.add_ConductingEquipment_Terminals(Terminal(Terminal_sequenceNumber=1+len(S1.ConductingEquipment_Terminals), Terminal_ConnectivityNode=t2.Terminal_ConnectivityNode))
    S3_AL1_feeder = Feeder(IdentifiedObject_mRID='S3_AL1')
    S3.add_ConductingEquipment_Terminals(Terminal(Terminal_sequenceNumber=1+len(S3.ConductingEquipment_Terminals), Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='S3_AL1')))
    S2_AL1_feeder = Feeder(IdentifiedObject_mRID='S2_AL1')
    S2.add_ConductingEquipment_Terminals(Terminal(Terminal_sequenceNumber=1+len(S2.ConductingEquipment_Terminals), Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='S2_AL1')))
    S2_AL2_feeder = Feeder(IdentifiedObject_mRID='S2_AL2')
    S2.add_ConductingEquipment_Terminals(Terminal(Terminal_sequenceNumber=1+len(S2.ConductingEquipment_Terminals), Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='S2_AL2')))
    S1_AL1_feeder = Feeder(IdentifiedObject_mRID='S1_AL1')
    S1.add_ConductingEquipment_Terminals(Terminal(Terminal_sequenceNumber=1+len(S1.ConductingEquipment_Terminals), Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='S1_AL1')))
    S1_AL2_feeder = Feeder(IdentifiedObject_mRID='S1_AL2')
    S1.add_ConductingEquipment_Terminals(Terminal(Terminal_sequenceNumber=1+len(S1.ConductingEquipment_Terminals), Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='S1_AL2')))
    S1_AL3_feeder = Feeder(IdentifiedObject_mRID='S1_AL3')
    S1.add_ConductingEquipment_Terminals(Terminal(Terminal_sequenceNumber=1+len(S1.ConductingEquipment_Terminals), Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='S1_AL3')))
    S1_AL4_feeder = Feeder(IdentifiedObject_mRID='S1_AL4')
    S1.add_ConductingEquipment_Terminals(Terminal(Terminal_sequenceNumber=1+len(S1.ConductingEquipment_Terminals), Terminal_ConnectivityNode=ConnectivityNode(IdentifiedObject_mRID='S1_AL4')))
    CH18N1 = ACLineSegment(IdentifiedObject_mRID='CH18N1', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('3.304')))
    CH17N1 = ACLineSegment(IdentifiedObject_mRID='CH17N1', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('5.08')))
    M1CH17 = ACLineSegment(IdentifiedObject_mRID='M1CH17', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('2.5305')))
    CH16M1 = ACLineSegment(IdentifiedObject_mRID='CH16M1', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('2.5305')))
    L1CH16 = ACLineSegment(IdentifiedObject_mRID='L1CH16', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.0015')))
    CH15L1 = ACLineSegment(IdentifiedObject_mRID='CH15L1', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.0015')))
    CH12K1 = ACLineSegment(IdentifiedObject_mRID='CH12K1', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('1.621')))
    D1CH5 = ACLineSegment(IdentifiedObject_mRID='D1CH5', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.510')))
    CH4D1 = ACLineSegment(IdentifiedObject_mRID='CH4D1', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.580')))
    C1CH4 = ACLineSegment(IdentifiedObject_mRID='C1CH4', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.910')))
    CH8K1 = ACLineSegment(IdentifiedObject_mRID='CH8K1', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('2.250')))
    K2K1 = ACLineSegment(IdentifiedObject_mRID='K2K1', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('2.156')))
    CH11K2 = ACLineSegment(IdentifiedObject_mRID='CH11K2', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('2.768')))
    CH3C1 = ACLineSegment(IdentifiedObject_mRID='CH3C1', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.910')))
    J1CH15 = ACLineSegment(IdentifiedObject_mRID='J1CH15', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.945')))
    H1CH11 = ACLineSegment(IdentifiedObject_mRID='H1CH11', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.941')))
    F1CH8 = ACLineSegment(IdentifiedObject_mRID='F1CH8', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.841')))
    B1CH3 = ACLineSegment(IdentifiedObject_mRID='B1CH3', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.595')))
    CH14J1 = ACLineSegment(IdentifiedObject_mRID='CH14J1', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.945')))
    CH10H1 = ACLineSegment(IdentifiedObject_mRID='CH10H1', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('3.173')))
    CH7F1 = ACLineSegment(IdentifiedObject_mRID='CH7F1', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.841')))
    CH2B1 = ACLineSegment(IdentifiedObject_mRID='CH2B1', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.595')))
    I1CH14 = ACLineSegment(IdentifiedObject_mRID='I1CH14', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('4.037')))
    G1CH10 = ACLineSegment(IdentifiedObject_mRID='G1CH10', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('999.5')))
    E1CH7 = ACLineSegment(IdentifiedObject_mRID='E1CH7', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('2.5825')))
    A1CH2 = ACLineSegment(IdentifiedObject_mRID='A1CH2', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('2.520')))
    CH13I1 = ACLineSegment(IdentifiedObject_mRID='CH13I1', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('5.039')))
    CH9G1 = ACLineSegment(IdentifiedObject_mRID='CH9G1', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.9995')))
    CH6E1 = ACLineSegment(IdentifiedObject_mRID='CH6E1', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('2.5825')))
    CH1A1 = ACLineSegment(IdentifiedObject_mRID='CH1A1', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('2.520')))
    S3CH18 = ACLineSegment(IdentifiedObject_mRID='S3CH18', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.01')))
    S2CH5 = ACLineSegment(IdentifiedObject_mRID='S2CH5', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.01')))
    S2CH12 = ACLineSegment(IdentifiedObject_mRID='S2CH12', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.01')))
    S1CH13 = ACLineSegment(IdentifiedObject_mRID='S1CH13', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.01')))
    S1CH9 = ACLineSegment(IdentifiedObject_mRID='S1CH9', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.01')))
    S1CH6 = ACLineSegment(IdentifiedObject_mRID='S1CH6', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.01')))
    S1CH1 = ACLineSegment(IdentifiedObject_mRID='S1CH1', ConductingEquipment_Terminals=[Terminal(Terminal_sequenceNumber=1), Terminal(Terminal_sequenceNumber=2)], Conductor_length=Length(UnitMultiplier('k'), UnitSymbol('m'), Decimal('0.01')))
    CCA2668MCM = PerLengthSequenceImpedance(IdentifiedObject_mRID='CCA 266.8 MCM', 
        PerLengthSequenceImpedance_r=ResistancePerLength(ResistancePerLength_multiplier=UnitMultiplier('none'), ResistancePerLength_unit=UnitSymbol('ohmPerm'), ResistancePerLength_value=Decimal('0.2391')),
        PerLengthSequenceImpedance_r0=ResistancePerLength(ResistancePerLength_multiplier=UnitMultiplier('none'), ResistancePerLength_unit=UnitSymbol('ohmPerm'), ResistancePerLength_value=Decimal('0.41693')),
        PerLengthSequenceImpedance_x=ReactancePerLength(ReactancePerLength_multiplier=UnitMultiplier('none'), ReactancePerLength_unit=UnitSymbol('ohmPerm'), ReactancePerLength_value=Decimal('0.37895')),
        PerLengthSequenceImpedance_x0=ReactancePerLength(ReactancePerLength_multiplier=UnitMultiplier('none'), ReactancePerLength_unit=UnitSymbol('ohmPerm'), ReactancePerLength_value=Decimal('1.55591'))
    )  
    CCA2668MCM_limit = OperationalLimitSet(IdentifiedObject_mRID='CCA 266.8 MCM', OperationalLimitSet_OperationalLimitValue=[CurrentLimit(CurrentLimit_value=CurrentFlow(CurrentFlow_multiplier=UnitMultiplier('none'), CurrentFlow_unit=UnitSymbol('A'), CurrentFlow_value=Decimal('475')))])
    SPACER240mm2 = PerLengthSequenceImpedance(IdentifiedObject_mRID='SPACER 240 mm2', 
        PerLengthSequenceImpedance_r=ResistancePerLength(ResistancePerLength_multiplier=UnitMultiplier('none'), ResistancePerLength_unit=UnitSymbol('ohmPerm'), ResistancePerLength_value=Decimal('0.141')),
        PerLengthSequenceImpedance_r0=ResistancePerLength(ResistancePerLength_multiplier=UnitMultiplier('none'), ResistancePerLength_unit=UnitSymbol('ohmPerm'), ResistancePerLength_value=Decimal('2.131')),
        PerLengthSequenceImpedance_x=ReactancePerLength(ReactancePerLength_multiplier=UnitMultiplier('none'), ReactancePerLength_unit=UnitSymbol('ohmPerm'), ReactancePerLength_value=Decimal('0.2762')),
        PerLengthSequenceImpedance_x0=ReactancePerLength(ReactancePerLength_multiplier=UnitMultiplier('none'), ReactancePerLength_unit=UnitSymbol('ohmPerm'), ReactancePerLength_value=Decimal('2.2615'))
    )  
    SPACER240mm2_limit = OperationalLimitSet(IdentifiedObject_mRID='SPACER 240 mm2', OperationalLimitSet_OperationalLimitValue=[CurrentLimit(CurrentLimit_value=CurrentFlow(CurrentFlow_multiplier=UnitMultiplier('none'), CurrentFlow_unit=UnitSymbol('A'), CurrentFlow_value=Decimal('617')))])
    CCA110AWG = PerLengthSequenceImpedance(IdentifiedObject_mRID='CCA 1/10 AWG', 
        PerLengthSequenceImpedance_r=ResistancePerLength(ResistancePerLength_multiplier=UnitMultiplier('none'), ResistancePerLength_unit=UnitSymbol('ohmPerm'), ResistancePerLength_value=Decimal('0.5877')),
        PerLengthSequenceImpedance_r0=ResistancePerLength(ResistancePerLength_multiplier=UnitMultiplier('none'), ResistancePerLength_unit=UnitSymbol('ohmPerm'), ResistancePerLength_value=Decimal('0.7653')),
        PerLengthSequenceImpedance_x=ReactancePerLength(ReactancePerLength_multiplier=UnitMultiplier('none'), ReactancePerLength_unit=UnitSymbol('ohmPerm'), ReactancePerLength_value=Decimal('0.4374')),
        PerLengthSequenceImpedance_x0=ReactancePerLength(ReactancePerLength_multiplier=UnitMultiplier('none'), ReactancePerLength_unit=UnitSymbol('ohmPerm'), ReactancePerLength_value=Decimal('1.6043'))
    )  
    CCA110AWG_limit = OperationalLimitSet(IdentifiedObject_mRID='CCA 1/10 AWG', OperationalLimitSet_OperationalLimitValue=[CurrentLimit(CurrentLimit_value=CurrentFlow(CurrentFlow_multiplier=UnitMultiplier('none'), CurrentFlow_unit=UnitSymbol('A'), CurrentFlow_value=Decimal('242')))])
    CU95mm2 = PerLengthSequenceImpedance(IdentifiedObject_mRID='CU 95 mm2', 
        PerLengthSequenceImpedance_r=ResistancePerLength(ResistancePerLength_multiplier=UnitMultiplier('none'), ResistancePerLength_unit=UnitSymbol('ohmPerm'), ResistancePerLength_value=Decimal('0.2213')),
        PerLengthSequenceImpedance_r0=ResistancePerLength(ResistancePerLength_multiplier=UnitMultiplier('none'), ResistancePerLength_unit=UnitSymbol('ohmPerm'), ResistancePerLength_value=Decimal('0.399')),
        PerLengthSequenceImpedance_x=ReactancePerLength(ReactancePerLength_multiplier=UnitMultiplier('none'), ReactancePerLength_unit=UnitSymbol('ohmPerm'), ReactancePerLength_value=Decimal('0.4101')),
        PerLengthSequenceImpedance_x0=ReactancePerLength(ReactancePerLength_multiplier=UnitMultiplier('none'), ReactancePerLength_unit=UnitSymbol('ohmPerm'), ReactancePerLength_value=Decimal('1.5771'))
    )  
    CU95mm2_limit = OperationalLimitSet(IdentifiedObject_mRID='CU 95 mm2', OperationalLimitSet_OperationalLimitValue=[CurrentLimit(CurrentLimit_value=CurrentFlow(CurrentFlow_multiplier=UnitMultiplier('none'), CurrentFlow_unit=UnitSymbol('A'), CurrentFlow_value=Decimal('438')))])
    cn_1 = CH18.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode
    cn_2 = N1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    CH18N1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    CH18N1.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    CH18N1.Equipment_OperationalLimitSet = [SPACER240mm2_limit]
    CH18N1.ACLineSegment_PerLengthImpedance = SPACER240mm2
    cn_1 = N1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    cn_2 = CH17.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    CH17N1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    CH17N1.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    CH17N1.Equipment_OperationalLimitSet = [CU95mm2_limit]
    CH17N1.ACLineSegment_PerLengthImpedance = CU95mm2
    cn_1 = CH17.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode
    cn_2 = M1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    M1CH17.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    M1CH17.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    M1CH17.Equipment_OperationalLimitSet = [CU95mm2_limit]
    M1CH17.ACLineSegment_PerLengthImpedance = CU95mm2
    cn_1 = M1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    cn_2 = CH16.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    CH16M1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    CH16M1.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    CH16M1.Equipment_OperationalLimitSet = [CU95mm2_limit]
    CH16M1.ACLineSegment_PerLengthImpedance = CU95mm2
    cn_1 = L1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    cn_2 = CH16.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode
    L1CH16.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    L1CH16.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    L1CH16.Equipment_OperationalLimitSet = [CU95mm2_limit]
    L1CH16.ACLineSegment_PerLengthImpedance = CU95mm2
    cn_1 = CH15.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode
    cn_2 = L1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    CH15L1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    CH15L1.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    CH15L1.Equipment_OperationalLimitSet = [CU95mm2_limit]
    CH15L1.ACLineSegment_PerLengthImpedance = CU95mm2
    cn_1 = CH12.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode
    cn_2 = K1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    CH12K1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    CH12K1.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    CH12K1.Equipment_OperationalLimitSet = [SPACER240mm2_limit]
    CH12K1.ACLineSegment_PerLengthImpedance = SPACER240mm2
    cn_1 = CH5.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode
    cn_2 = D1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    D1CH5.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    D1CH5.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    D1CH5.Equipment_OperationalLimitSet = [SPACER240mm2_limit]
    D1CH5.ACLineSegment_PerLengthImpedance = SPACER240mm2
    cn_1 = D1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    cn_2 = CH4.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    CH4D1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    CH4D1.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    CH4D1.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    CH4D1.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_1 = CH4.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode
    cn_2 = C1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    C1CH4.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    C1CH4.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    C1CH4.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    C1CH4.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_1 = K1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    cn_2 = CH8.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    CH8K1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    CH8K1.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    CH8K1.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    CH8K1.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_1 = K1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    cn_2 = K2.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    K2K1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    K2K1.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    K2K1.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    K2K1.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_1 = K2.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    cn_2 = CH11.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    CH11K2.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    CH11K2.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    CH11K2.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    CH11K2.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_1 = C1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    cn_2 = CH3.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    CH3C1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    CH3C1.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    CH3C1.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    CH3C1.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_1 = J1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    cn_2 = CH15.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    J1CH15.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    J1CH15.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    J1CH15.Equipment_OperationalLimitSet = [CU95mm2_limit]
    J1CH15.ACLineSegment_PerLengthImpedance = CU95mm2
    cn_1 = H1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    cn_2 = CH11.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode
    H1CH11.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    H1CH11.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    H1CH11.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    H1CH11.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_1 = F1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    cn_2 = CH8.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode
    F1CH8.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    F1CH8.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    F1CH8.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    F1CH8.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_1 = B1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    cn_2 = CH3.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode
    B1CH3.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    B1CH3.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    B1CH3.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    B1CH3.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_1 = CH14.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode
    cn_2 = J1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    CH14J1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    CH14J1.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    CH14J1.Equipment_OperationalLimitSet = [CU95mm2_limit]
    CH14J1.ACLineSegment_PerLengthImpedance = CU95mm2
    cn_1 = CH10.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode
    cn_2 = H1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    CH10H1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    CH10H1.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    CH10H1.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    CH10H1.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_1 = CH7.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode
    cn_2 = F1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    CH7F1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    CH7F1.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    CH7F1.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    CH7F1.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_1 = CH2.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode
    cn_2 = B1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    CH2B1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    CH2B1.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    CH2B1.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    CH2B1.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_1 = I1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    cn_2 = CH14.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    I1CH14.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    I1CH14.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    I1CH14.Equipment_OperationalLimitSet = [CU95mm2_limit]
    I1CH14.ACLineSegment_PerLengthImpedance = CU95mm2
    cn_1 = G1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    cn_2 = CH10.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    G1CH10.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    G1CH10.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    G1CH10.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    G1CH10.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_1 = E1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    cn_2 = CH7.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    E1CH7.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    E1CH7.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    E1CH7.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    E1CH7.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_1 = A1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    cn_2 = CH2.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    A1CH2.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    A1CH2.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    A1CH2.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    A1CH2.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_1 = CH13.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode
    cn_2 = I1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    CH13I1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    CH13I1.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    CH13I1.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    CH13I1.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_1 = CH9.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode
    cn_2 = G1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    CH9G1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    CH9G1.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    CH9G1.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    CH9G1.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_1 = CH6.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode
    cn_2 = E1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    CH6E1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    CH6E1.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    CH6E1.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    CH6E1.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_1 = CH1.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode
    cn_2 = A1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    CH1A1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    CH1A1.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    CH1A1.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    CH1A1.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_eqs = [[eq.Terminal_ConductingEquipment for eq in tt.Terminal_ConnectivityNode.ConnectivityNode_Terminals] for tt in S3.ConductingEquipment_Terminals]
    idx = next(i for i in range(len(cn_eqs)) if len(cn_eqs[i]) == 1)
    cn_1 = S3.ConductingEquipment_Terminals[idx].Terminal_ConnectivityNode
    cn_2 = CH18.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    S3CH18.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    S3CH18.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    S3CH18.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    S3CH18.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_eqs = [[eq.Terminal_ConductingEquipment for eq in tt.Terminal_ConnectivityNode.ConnectivityNode_Terminals] for tt in S2.ConductingEquipment_Terminals]
    idx = next(i for i in range(len(cn_eqs)) if len(cn_eqs[i]) == 1)
    cn_1 = S2.ConductingEquipment_Terminals[idx].Terminal_ConnectivityNode
    cn_2 = CH5.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    S2CH5.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    S2CH5.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    S2CH5.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    S2CH5.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_eqs = [[eq.Terminal_ConductingEquipment for eq in tt.Terminal_ConnectivityNode.ConnectivityNode_Terminals] for tt in S2.ConductingEquipment_Terminals]
    idx = next(i for i in range(len(cn_eqs)) if len(cn_eqs[i]) == 1)
    cn_1 = S2.ConductingEquipment_Terminals[idx].Terminal_ConnectivityNode
    cn_2 = CH12.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    S2CH12.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    S2CH12.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    S2CH12.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    S2CH12.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_eqs = [[eq.Terminal_ConductingEquipment for eq in tt.Terminal_ConnectivityNode.ConnectivityNode_Terminals] for tt in S1.ConductingEquipment_Terminals]
    idx = next(i for i in range(len(cn_eqs)) if len(cn_eqs[i]) == 1)
    cn_1 = S1.ConductingEquipment_Terminals[idx].Terminal_ConnectivityNode
    cn_2 = CH13.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    S1CH13.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    S1CH13.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    S1CH13.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    S1CH13.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_eqs = [[eq.Terminal_ConductingEquipment for eq in tt.Terminal_ConnectivityNode.ConnectivityNode_Terminals] for tt in S1.ConductingEquipment_Terminals]
    idx = next(i for i in range(len(cn_eqs)) if len(cn_eqs[i]) == 1)
    cn_1 = S1.ConductingEquipment_Terminals[idx].Terminal_ConnectivityNode
    cn_2 = CH9.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    S1CH9.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    S1CH9.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    S1CH9.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    S1CH9.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_eqs = [[eq.Terminal_ConductingEquipment for eq in tt.Terminal_ConnectivityNode.ConnectivityNode_Terminals] for tt in S1.ConductingEquipment_Terminals]
    idx = next(i for i in range(len(cn_eqs)) if len(cn_eqs[i]) == 1)
    cn_1 = S1.ConductingEquipment_Terminals[idx].Terminal_ConnectivityNode
    cn_2 = CH6.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    S1CH6.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    S1CH6.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    S1CH6.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    S1CH6.ACLineSegment_PerLengthImpedance = CCA2668MCM
    cn_eqs = [[eq.Terminal_ConductingEquipment for eq in tt.Terminal_ConnectivityNode.ConnectivityNode_Terminals] for tt in S1.ConductingEquipment_Terminals]
    idx = next(i for i in range(len(cn_eqs)) if len(cn_eqs[i]) == 1)
    cn_1 = S1.ConductingEquipment_Terminals[idx].Terminal_ConnectivityNode
    cn_2 = CH1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode
    S1CH1.ConductingEquipment_Terminals[0].Terminal_ConnectivityNode = cn_1
    S1CH1.ConductingEquipment_Terminals[1].Terminal_ConnectivityNode = cn_2
    S1CH1.Equipment_OperationalLimitSet = [CCA2668MCM_limit]
    S1CH1.ACLineSegment_PerLengthImpedance = CCA2668MCM
    S3_AL1_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_N)
    S3_AL1_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_S3)
    S3_AL1_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_M)
    S2_AL1_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_D)
    S2_AL1_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_S2)
    S2_AL1_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_C)
    S2_AL2_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_K)
    S2_AL2_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_S2)
    S1_AL1_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_I)
    S1_AL1_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_S1)
    S1_AL1_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_J)
    S1_AL1_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_L)
    S1_AL2_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_G)
    S1_AL2_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_S1)
    S1_AL2_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_H)
    S1_AL3_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_E)
    S1_AL3_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_S1)
    S1_AL3_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_F)
    S1_AL4_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_A)
    S1_AL4_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_S1)
    S1_AL4_feeder.add_ConnectivityNodeContainer_TopologicalNode(setor_B)
    to_visit = [terminal.Terminal_ConnectivityNode for terminal in S3.ConductingEquipment_Terminals] # cn to visit
    while len(to_visit):
        cn = to_visit.pop(0)
        setor_S3.add_TopologicalNode_ConnectivityNodes(cn)
        for terminal in cn.ConnectivityNode_Terminals:
            equipment = terminal.Terminal_ConductingEquipment
            if isinstance(equipment, ACLineSegment):
                other_terminal = list(filter(lambda term: id(term) != id(terminal), equipment.ConductingEquipment_Terminals))[0]
                other_cn = other_terminal.Terminal_ConnectivityNode
                if other_cn not in setor_S3.TopologicalNode_ConnectivityNodes:
                    to_visit.append(other_cn)
    to_visit = [terminal.Terminal_ConnectivityNode for terminal in K1.ConductingEquipment_Terminals] # cn to visit
    while len(to_visit):
        cn = to_visit.pop(0)
        setor_K.add_TopologicalNode_ConnectivityNodes(cn)
        for terminal in cn.ConnectivityNode_Terminals:
            equipment = terminal.Terminal_ConductingEquipment
            if isinstance(equipment, ACLineSegment):
                other_terminal = list(filter(lambda term: id(term) != id(terminal), equipment.ConductingEquipment_Terminals))[0]
                other_cn = other_terminal.Terminal_ConnectivityNode
                if other_cn not in setor_K.TopologicalNode_ConnectivityNodes:
                    to_visit.append(other_cn)
    to_visit = [terminal.Terminal_ConnectivityNode for terminal in K2.ConductingEquipment_Terminals] # cn to visit
    while len(to_visit):
        cn = to_visit.pop(0)
        setor_K.add_TopologicalNode_ConnectivityNodes(cn)
        for terminal in cn.ConnectivityNode_Terminals:
            equipment = terminal.Terminal_ConductingEquipment
            if isinstance(equipment, ACLineSegment):
                other_terminal = list(filter(lambda term: id(term) != id(terminal), equipment.ConductingEquipment_Terminals))[0]
                other_cn = other_terminal.Terminal_ConnectivityNode
                if other_cn not in setor_K.TopologicalNode_ConnectivityNodes:
                    to_visit.append(other_cn)
    to_visit = [terminal.Terminal_ConnectivityNode for terminal in H1.ConductingEquipment_Terminals] # cn to visit
    while len(to_visit):
        cn = to_visit.pop(0)
        setor_H.add_TopologicalNode_ConnectivityNodes(cn)
        for terminal in cn.ConnectivityNode_Terminals:
            equipment = terminal.Terminal_ConductingEquipment
            if isinstance(equipment, ACLineSegment):
                other_terminal = list(filter(lambda term: id(term) != id(terminal), equipment.ConductingEquipment_Terminals))[0]
                other_cn = other_terminal.Terminal_ConnectivityNode
                if other_cn not in setor_H.TopologicalNode_ConnectivityNodes:
                    to_visit.append(other_cn)
    to_visit = [terminal.Terminal_ConnectivityNode for terminal in C1.ConductingEquipment_Terminals] # cn to visit
    while len(to_visit):
        cn = to_visit.pop(0)
        setor_C.add_TopologicalNode_ConnectivityNodes(cn)
        for terminal in cn.ConnectivityNode_Terminals:
            equipment = terminal.Terminal_ConductingEquipment
            if isinstance(equipment, ACLineSegment):
                other_terminal = list(filter(lambda term: id(term) != id(terminal), equipment.ConductingEquipment_Terminals))[0]
                other_cn = other_terminal.Terminal_ConnectivityNode
                if other_cn not in setor_C.TopologicalNode_ConnectivityNodes:
                    to_visit.append(other_cn)
    to_visit = [terminal.Terminal_ConnectivityNode for terminal in L1.ConductingEquipment_Terminals] # cn to visit
    while len(to_visit):
        cn = to_visit.pop(0)
        setor_L.add_TopologicalNode_ConnectivityNodes(cn)
        for terminal in cn.ConnectivityNode_Terminals:
            equipment = terminal.Terminal_ConductingEquipment
            if isinstance(equipment, ACLineSegment):
                other_terminal = list(filter(lambda term: id(term) != id(terminal), equipment.ConductingEquipment_Terminals))[0]
                other_cn = other_terminal.Terminal_ConnectivityNode
                if other_cn not in setor_L.TopologicalNode_ConnectivityNodes:
                    to_visit.append(other_cn)
    to_visit = [terminal.Terminal_ConnectivityNode for terminal in J1.ConductingEquipment_Terminals] # cn to visit
    while len(to_visit):
        cn = to_visit.pop(0)
        setor_J.add_TopologicalNode_ConnectivityNodes(cn)
        for terminal in cn.ConnectivityNode_Terminals:
            equipment = terminal.Terminal_ConductingEquipment
            if isinstance(equipment, ACLineSegment):
                other_terminal = list(filter(lambda term: id(term) != id(terminal), equipment.ConductingEquipment_Terminals))[0]
                other_cn = other_terminal.Terminal_ConnectivityNode
                if other_cn not in setor_J.TopologicalNode_ConnectivityNodes:
                    to_visit.append(other_cn)
    to_visit = [terminal.Terminal_ConnectivityNode for terminal in M1.ConductingEquipment_Terminals] # cn to visit
    while len(to_visit):
        cn = to_visit.pop(0)
        setor_M.add_TopologicalNode_ConnectivityNodes(cn)
        for terminal in cn.ConnectivityNode_Terminals:
            equipment = terminal.Terminal_ConductingEquipment
            if isinstance(equipment, ACLineSegment):
                other_terminal = list(filter(lambda term: id(term) != id(terminal), equipment.ConductingEquipment_Terminals))[0]
                other_cn = other_terminal.Terminal_ConnectivityNode
                if other_cn not in setor_M.TopologicalNode_ConnectivityNodes:
                    to_visit.append(other_cn)
    to_visit = [terminal.Terminal_ConnectivityNode for terminal in D1.ConductingEquipment_Terminals] # cn to visit
    while len(to_visit):
        cn = to_visit.pop(0)
        setor_D.add_TopologicalNode_ConnectivityNodes(cn)
        for terminal in cn.ConnectivityNode_Terminals:
            equipment = terminal.Terminal_ConductingEquipment
            if isinstance(equipment, ACLineSegment):
                other_terminal = list(filter(lambda term: id(term) != id(terminal), equipment.ConductingEquipment_Terminals))[0]
                other_cn = other_terminal.Terminal_ConnectivityNode
                if other_cn not in setor_D.TopologicalNode_ConnectivityNodes:
                    to_visit.append(other_cn)
    to_visit = [terminal.Terminal_ConnectivityNode for terminal in N1.ConductingEquipment_Terminals] # cn to visit
    while len(to_visit):
        cn = to_visit.pop(0)
        setor_N.add_TopologicalNode_ConnectivityNodes(cn)
        for terminal in cn.ConnectivityNode_Terminals:
            equipment = terminal.Terminal_ConductingEquipment
            if isinstance(equipment, ACLineSegment):
                other_terminal = list(filter(lambda term: id(term) != id(terminal), equipment.ConductingEquipment_Terminals))[0]
                other_cn = other_terminal.Terminal_ConnectivityNode
                if other_cn not in setor_N.TopologicalNode_ConnectivityNodes:
                    to_visit.append(other_cn)
    to_visit = [terminal.Terminal_ConnectivityNode for terminal in F1.ConductingEquipment_Terminals] # cn to visit
    while len(to_visit):
        cn = to_visit.pop(0)
        setor_F.add_TopologicalNode_ConnectivityNodes(cn)
        for terminal in cn.ConnectivityNode_Terminals:
            equipment = terminal.Terminal_ConductingEquipment
            if isinstance(equipment, ACLineSegment):
                other_terminal = list(filter(lambda term: id(term) != id(terminal), equipment.ConductingEquipment_Terminals))[0]
                other_cn = other_terminal.Terminal_ConnectivityNode
                if other_cn not in setor_F.TopologicalNode_ConnectivityNodes:
                    to_visit.append(other_cn)
    to_visit = [terminal.Terminal_ConnectivityNode for terminal in B1.ConductingEquipment_Terminals] # cn to visit
    while len(to_visit):
        cn = to_visit.pop(0)
        setor_B.add_TopologicalNode_ConnectivityNodes(cn)
        for terminal in cn.ConnectivityNode_Terminals:
            equipment = terminal.Terminal_ConductingEquipment
            if isinstance(equipment, ACLineSegment):
                other_terminal = list(filter(lambda term: id(term) != id(terminal), equipment.ConductingEquipment_Terminals))[0]
                other_cn = other_terminal.Terminal_ConnectivityNode
                if other_cn not in setor_B.TopologicalNode_ConnectivityNodes:
                    to_visit.append(other_cn)
    to_visit = [terminal.Terminal_ConnectivityNode for terminal in I1.ConductingEquipment_Terminals] # cn to visit
    while len(to_visit):
        cn = to_visit.pop(0)
        setor_I.add_TopologicalNode_ConnectivityNodes(cn)
        for terminal in cn.ConnectivityNode_Terminals:
            equipment = terminal.Terminal_ConductingEquipment
            if isinstance(equipment, ACLineSegment):
                other_terminal = list(filter(lambda term: id(term) != id(terminal), equipment.ConductingEquipment_Terminals))[0]
                other_cn = other_terminal.Terminal_ConnectivityNode
                if other_cn not in setor_I.TopologicalNode_ConnectivityNodes:
                    to_visit.append(other_cn)
    to_visit = [terminal.Terminal_ConnectivityNode for terminal in G1.ConductingEquipment_Terminals] # cn to visit
    while len(to_visit):
        cn = to_visit.pop(0)
        setor_G.add_TopologicalNode_ConnectivityNodes(cn)
        for terminal in cn.ConnectivityNode_Terminals:
            equipment = terminal.Terminal_ConductingEquipment
            if isinstance(equipment, ACLineSegment):
                other_terminal = list(filter(lambda term: id(term) != id(terminal), equipment.ConductingEquipment_Terminals))[0]
                other_cn = other_terminal.Terminal_ConnectivityNode
                if other_cn not in setor_G.TopologicalNode_ConnectivityNodes:
                    to_visit.append(other_cn)
    to_visit = [terminal.Terminal_ConnectivityNode for terminal in E1.ConductingEquipment_Terminals] # cn to visit
    while len(to_visit):
        cn = to_visit.pop(0)
        setor_E.add_TopologicalNode_ConnectivityNodes(cn)
        for terminal in cn.ConnectivityNode_Terminals:
            equipment = terminal.Terminal_ConductingEquipment
            if isinstance(equipment, ACLineSegment):
                other_terminal = list(filter(lambda term: id(term) != id(terminal), equipment.ConductingEquipment_Terminals))[0]
                other_cn = other_terminal.Terminal_ConnectivityNode
                if other_cn not in setor_E.TopologicalNode_ConnectivityNodes:
                    to_visit.append(other_cn)
    to_visit = [terminal.Terminal_ConnectivityNode for terminal in A1.ConductingEquipment_Terminals] # cn to visit
    while len(to_visit):
        cn = to_visit.pop(0)
        setor_A.add_TopologicalNode_ConnectivityNodes(cn)
        for terminal in cn.ConnectivityNode_Terminals:
            equipment = terminal.Terminal_ConductingEquipment
            if isinstance(equipment, ACLineSegment):
                other_terminal = list(filter(lambda term: id(term) != id(terminal), equipment.ConductingEquipment_Terminals))[0]
                other_cn = other_terminal.Terminal_ConnectivityNode
                if other_cn not in setor_A.TopologicalNode_ConnectivityNodes:
                    to_visit.append(other_cn)
    to_visit = [terminal.Terminal_ConnectivityNode for terminal in S2.ConductingEquipment_Terminals] # cn to visit
    while len(to_visit):
        cn = to_visit.pop(0)
        setor_S2.add_TopologicalNode_ConnectivityNodes(cn)
        for terminal in cn.ConnectivityNode_Terminals:
            equipment = terminal.Terminal_ConductingEquipment
            if isinstance(equipment, ACLineSegment):
                other_terminal = list(filter(lambda term: id(term) != id(terminal), equipment.ConductingEquipment_Terminals))[0]
                other_cn = other_terminal.Terminal_ConnectivityNode
                if other_cn not in setor_S2.TopologicalNode_ConnectivityNodes:
                    to_visit.append(other_cn)
    to_visit = [terminal.Terminal_ConnectivityNode for terminal in S1.ConductingEquipment_Terminals] # cn to visit
    while len(to_visit):
        cn = to_visit.pop(0)
        setor_S1.add_TopologicalNode_ConnectivityNodes(cn)
        for terminal in cn.ConnectivityNode_Terminals:
            equipment = terminal.Terminal_ConductingEquipment
            if isinstance(equipment, ACLineSegment):
                other_terminal = list(filter(lambda term: id(term) != id(terminal), equipment.ConductingEquipment_Terminals))[0]
                other_cn = other_terminal.Terminal_ConnectivityNode
                if other_cn not in setor_S1.TopologicalNode_ConnectivityNodes:
                    to_visit.append(other_cn)
    subestacao_S3.add_Substation_SubstationFeeder(S3_AL1_feeder)
    subestacao_S3.add_EquipmentContainer_Equipments(S3_T1)
    subestacao_S3.add_EquipmentContainer_Equipments(S3_T2)
    subestacao_S2.add_Substation_SubstationFeeder(S2_AL1_feeder)
    subestacao_S2.add_Substation_SubstationFeeder(S2_AL2_feeder)
    subestacao_S2.add_EquipmentContainer_Equipments(S2_T1)
    subestacao_S1.add_Substation_SubstationFeeder(S1_AL1_feeder)
    subestacao_S1.add_Substation_SubstationFeeder(S1_AL2_feeder)
    subestacao_S1.add_Substation_SubstationFeeder(S1_AL3_feeder)
    subestacao_S1.add_Substation_SubstationFeeder(S1_AL4_feeder)
    subestacao_S1.add_EquipmentContainer_Equipments(S1_T1)
    subestacao_S1.add_EquipmentContainer_Equipments(S1_T2)

    elements = list(filter(lambda elem: elem.__class__.__module__ == 'rede.network', locals().values()))
    doc = DocumentCIMRDF()
    doc.add_recursively(elements)
    doc.tofile('./rede/rede-cim.xml')
net()
