from decimal import Decimal

from cim_profile.network_v2_0 import ACLineSegment as ACLineSegmentSuper
from cim_profile.network_v2_0 import (ActivePower, ApparentPower,
                                      ApparentPowerLimit, BaseVoltage)
from cim_profile.network_v2_0 import BusbarSection as BusbarSectionSuper
from cim_profile.network_v2_0 import (ConductingEquipment, ConnectivityNode,
                                      CurrentFlow, CurrentLimit,
                                      DocumentCIMRDF)
from cim_profile.network_v2_0 import EnergyConsumer as EnergyConsumerSuper
from cim_profile.network_v2_0 import \
    EquivalentInjection as EquivalentInjectionSuper
from cim_profile.network_v2_0 import (Feeder, Length, OperationalLimitSet,
                                      PerLengthSequenceImpedance)
from cim_profile.network_v2_0 import PowerTransformer as PowerTransformerSuper
from cim_profile.network_v2_0 import (PowerTransformerEnd, Reactance,
                                      ReactancePerLength, ReactivePower,
                                      Resistance, ResistancePerLength,
                                      Substation)
from cim_profile.network_v2_0 import Switch as SwitchSuper
from cim_profile.network_v2_0 import Terminal, TopologicalNode, Voltage


class ConductingEquipmentExtension(ConductingEquipment):
    def __init__(self, max_terminals=50):
        self.max_terminals = max_terminals

    def create_Terminals(self, qty: int):
        for i in range(qty):
            self.Terminals.append(Terminal(sequenceNumber=i))

    def get_next_terminal(self):
        if len(self.Terminals) == self.max_terminals:
            raise Exception(f'All {self.max_terminals} terminals attributed')
        return Terminal(
            ConductingEquipment=self,
            sequenceNumber=len(self.Terminals)+1
        )

    def link_to(self, *others, feeder=None):
        try:
            assert not isinstance(self, Switch)
            topological_node = next(
                terminal.ConnectivityNode.TopologicalNode for terminal in self.Terminals if terminal.ConnectivityNode.TopologicalNode)
            topological_node.ConnectivityNodeContainer = feeder
        except:
            topological_node = TopologicalNode(
                mRID=f'node_{self.mRID}',
                ConnectivityNodeContainer=feeder,
            )

        ConnectivityNode(
            mRID=f'{self.mRID}-{others[-1].mRID}',
            Terminals=[self.get_next_terminal()] + [other.get_next_terminal()
                                                    for other in others],
            TopologicalNode=topological_node,
        )
        return others if len(others) > 1 else others[0]

    def get_ConnectivityNode_with(self, other: 'ConductingEquipmentExtension') -> ConnectivityNode:
        return next(t1.ConnectivityNode for t1 in self.Terminals for t2 in other.Terminals if t1.ConnectivityNode == t2.ConnectivityNode)

    def insert_between(self, other1: 'ConductingEquipmentExtension', other2: 'ConductingEquipmentExtension'):
        common_cn = other1.get_ConnectivityNode_with(other2)
        common_cn.add_Terminals(self.get_next_terminal())
        return common_cn


class ACLineSegment(ConductingEquipmentExtension, ACLineSegmentSuper):
    def __init__(self, *args, **kwargs):
        ACLineSegmentSuper.__init__(self, *args, **kwargs)
        ConductingEquipmentExtension.__init__(self, 2)


class BusbarSection(ConductingEquipmentExtension, BusbarSectionSuper):
    def __init__(self, *args, **kwargs):
        BusbarSectionSuper.__init__(self, *args, **kwargs)
        ConductingEquipmentExtension.__init__(self)


class EnergyConsumer(ConductingEquipmentExtension, EnergyConsumerSuper):
    def __init__(self, *args, **kwargs):
        EnergyConsumerSuper.__init__(self, *args, **kwargs)
        ConductingEquipmentExtension.__init__(self, 1)


class Switch(ConductingEquipmentExtension, SwitchSuper):
    def __init__(self, *args, **kwargs):
        SwitchSuper.__init__(self, *args, **kwargs)
        ConductingEquipmentExtension.__init__(self, 2)


class PowerTransformer(ConductingEquipmentExtension, PowerTransformerSuper):
    def __init__(self, *args, **kwargs):
        PowerTransformerSuper.__init__(self, *args, **kwargs)
        ConductingEquipmentExtension.__init__(self, 2)


class EquivalentInjection(ConductingEquipmentExtension, EquivalentInjectionSuper):
    def __init__(self, *args, **kwargs):
        EquivalentInjectionSuper.__init__(self, *args, **kwargs)
        ConductingEquipmentExtension.__init__(self, 1)


base_voltage_1 = BaseVoltage(
    Voltage('k', 'V', '69')
)
base_voltage_2 = BaseVoltage(
    Voltage('k', 'V', '13.8')
)

conductor1_impedance = PerLengthSequenceImpedance(
    mRID='AWG Copper',
    r=ResistancePerLength('m', 'ohmPerm', '10'),
    r0=ResistancePerLength('m', 'ohmPerm', '10'),
    x=ReactancePerLength('m', 'ohmPerm', '10'),
    x0=ReactancePerLength('m', 'ohmPerm', '10')
)
conductor1_limits = OperationalLimitSet(
    mRID='AWG Copper',
    OperationalLimitValue=[
        CurrentLimit(CurrentFlow('none', 'A', '600'))
    ]
)

##
substation1 = Substation(mRID='AQZ', name='Aquiraz')
busbar_s1 = BusbarSection(mRID='AQZ-busbar', EquipmentContainer=substation1)
transformer1_s1, transformer2_s1 = EquivalentInjection(
    mRID='EI1',
    BaseVoltage=base_voltage_1
).link_to(
    PowerTransformer(
        mRID='AQZ-01T1',
        PowerTransformerEnd=[
            PowerTransformerEnd(
                endNumber=1,
                connectionKind='D',
                ratedS=ApparentPower('M', 'VA', '15'),
                ratedU=Voltage('k', 'V', '69'),
                r=Resistance('m', 'ohm', '10'),
                r0=Resistance('m', 'ohm', '10'),
                x=Reactance('m', 'ohm', '10'),
                x0=Reactance('m', 'ohm', '10'),
            ),
            PowerTransformerEnd(
                endNumber=2,
                connectionKind='D',
                ratedS=ApparentPower('M', 'VA', '15'),
                ratedU=Voltage('k', 'V', '13.8')
            )
        ],
        EquipmentContainer=substation1
    ),
    PowerTransformer(
        mRID='AQZ-01T2',
        PowerTransformerEnd=[
            PowerTransformerEnd(
                endNumber=1,
                connectionKind='D',
                ratedS=ApparentPower('M', 'VA', '15'),
                ratedU=Voltage('k', 'V', '69'),
                r=Resistance('m', 'ohm', '10'),
                r0=Resistance('m', 'ohm', '10'),
                x=Reactance('m', 'ohm', '10'),
                x0=Reactance('m', 'ohm', '10'),
            ),
            PowerTransformerEnd(
                endNumber=2,
                connectionKind='D',
                ratedS=ApparentPower('M', 'VA', '15'),
                ratedU=Voltage('k', 'V', '13.8')
            )
        ],
        EquipmentContainer=substation1
    )
)
transformer1_s1.link_to(
    Switch(
        mRID='AQZ-11T1',
        normalOpen=False,
        open=False
    )
).link_to(busbar_s1)
transformer2_s1.link_to(
    Switch(
        mRID='AQZ-11T2',
        normalOpen=False,
        open=False
    )
).link_to(busbar_s1)

feeder_1_s1 = Feeder(mRID='AQZ_01I7', FeedingSubstation=substation1)
_, segment_B1_r1, segment_B1_tie1 = busbar_s1.link_to(
    ACLineSegment(
        mRID='AQZ-21I7',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_1_s1
).link_to(
    Switch(
        mRID='AQZ-21I7',
        normalOpen=False,
        open=False,
    ),
    feeder=feeder_1_s1
).link_to(
    ACLineSegment(
        mRID='21I7-B1',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_1_s1
).link_to(
    EnergyConsumer(
        mRID='B1',
        p=ActivePower('M', 'W', '1.0'),
        q=ReactivePower('M', 'VAr', '0.1')
    ),
    ACLineSegment(
        mRID='B1-R1',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    ACLineSegment(
        mRID='B1-Tie1',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_1_s1
)  # B1, B1_r1, B1_tie1
switch_tie3 = segment_B1_r1.link_to(
    Switch(
        mRID='R1',
        normalOpen=False,
        open=False,
    ),
    feeder=feeder_1_s1
).link_to(
    ACLineSegment(
        mRID='R1-B2',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_1_s1
).link_to(
    EnergyConsumer(
        mRID='B2',
        p=ActivePower('M', 'W', '1.0'),
        q=ReactivePower('M', 'VAr', '0.1')
    ),
    ACLineSegment(
        mRID='B2-Tie3',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_1_s1
)[1].link_to(
    Switch(
        mRID='Tie3',
        normalOpen=True,
        open=True,
    ),
    feeder=feeder_1_s1
)
switch_tie1 = segment_B1_tie1.link_to(
    Switch(
        mRID='Tie1',
        normalOpen=True,
        open=True,
    ),
    feeder=feeder_1_s1)

feeder_2_s1 = Feeder(mRID='AQZ_01I6', FeedingSubstation=substation1)
_, segment_B4_tie1, segment_B4_tie2, segment_B4_r2 = busbar_s1.link_to(
    ACLineSegment(
        mRID='AQZ-21I6',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_2_s1
).link_to(
    Switch(
        mRID='AQZ-21I6',
        normalOpen=False,
        open=False,
    ),
    feeder=feeder_2_s1
).link_to(
    ACLineSegment(
        mRID='21I6-B4',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_2_s1
).link_to(
    EnergyConsumer(
        mRID='B4',
        p=ActivePower('M', 'W', '1.0'),
        q=ReactivePower('M', 'VAr', '0.1')
    ),
    ACLineSegment(
        mRID='B4-Tie1',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    ACLineSegment(
        mRID='B4-Tie2',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    ACLineSegment(
        mRID='B4-R2',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_2_s1
)
segment_B4_tie1.link_to(switch_tie1)
switch_tie2 = segment_B4_tie2.link_to(
    Switch(
        mRID='Tie2',
        normalOpen=True,
        open=True,
    ),
    feeder=feeder_2_s1)
switch_tie4 = segment_B4_r2.link_to(
    Switch(
        mRID='R2',
        normalOpen=False,
        open=False,
    ),
    feeder=feeder_2_s1
).link_to(
    ACLineSegment(
        mRID='R2-B5',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_2_s1
).link_to(
    EnergyConsumer(
        mRID='B5',
        p=ActivePower('M', 'W', '1.0'),
        q=ReactivePower('M', 'VAr', '0.1')
    ),
    ACLineSegment(
        mRID='B5-Tie4',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_2_s1
)[1].link_to(
    Switch(
        mRID='Tie4',
        normalOpen=True,
        open=True,
    ),
    feeder=feeder_2_s1
)

feeder_3_s1 = Feeder(mRID='AQZ_01I5', FeedingSubstation=substation1)
B8, B8_tie2, B8_r4 = busbar_s1.link_to(
    ACLineSegment(
        mRID='AQZ-21I5',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_3_s1
).link_to(
    Switch(
        mRID='AQZ-21I5',
        normalOpen=False,
        open=False,
    ),
    feeder=feeder_3_s1
).link_to(
    ACLineSegment(
        mRID='21I5-B7',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_3_s1
).link_to(
    EnergyConsumer(
        mRID='B7',
        p=ActivePower('M', 'W', '1.0'),
        q=ReactivePower('M', 'VAr', '0.1')
    ),
    ACLineSegment(
        mRID='B7-R3',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_3_s1
)[1].link_to(
    Switch(
        mRID='R3',
        normalOpen=False,
        open=False,
    ),
    feeder=feeder_3_s1
).link_to(
    ACLineSegment(
        mRID='R3-B8',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_3_s1
).link_to(
    EnergyConsumer(
        mRID='B8',
        p=ActivePower('M', 'W', '1.0'),
        q=ReactivePower('M', 'VAr', '0.1')
    ),
    ACLineSegment(
        mRID='B8-Tie2',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    ACLineSegment(
        mRID='B8-R4',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_3_s1
)  # B8, B8_tie2, B8_r4
B8_tie2.link_to(switch_tie2)
switch_tie5 = B8_r4.link_to(
    Switch(
        mRID='R4',
        normalOpen=False,
        open=False,
    ),
    feeder=feeder_3_s1
).link_to(
    ACLineSegment(
        mRID='R4-B9',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_3_s1
).link_to(
    EnergyConsumer(
        mRID='B9',
        p=ActivePower('M', 'W', '1.0'),
        q=ReactivePower('M', 'VAr', '0.1')
    ),
    ACLineSegment(
        mRID='B9-Tie5',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_3_s1
)[1].link_to(
    Switch(
        mRID='Tie5',
        normalOpen=True,
        open=True,
    ),
    feeder=feeder_3_s1
)

feeder_4_s1 = Feeder(mRID='AQZ_01I4', FeedingSubstation=substation1)
switch_tie6 = busbar_s1.link_to(
    ACLineSegment(
        mRID='AQZ-busbar-21I4',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_4_s1
).link_to(
    Switch(
        mRID='AQZ-21I4',
        normalOpen=False,
        open=False,
    ),
    feeder=feeder_4_s1
).link_to(
    ACLineSegment(
        mRID='21I4-B11',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_4_s1
).link_to(
    EnergyConsumer(
        mRID='B11',
        p=ActivePower('M', 'W', '1.0'),
        q=ReactivePower('M', 'VAr', '0.1')
    ),
    ACLineSegment(
        mRID='B11-R5',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_4_s1
)[1].link_to(
    Switch(
        mRID='R5',
        normalOpen=False,
        open=False,
    ),
    feeder=feeder_4_s1
).link_to(
    ACLineSegment(
        mRID='R5-B12',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_4_s1
).link_to(
    EnergyConsumer(
        mRID='B12',
        p=ActivePower('M', 'W', '1.0'),
        q=ReactivePower('M', 'VAr', '0.1')
    ),
    ACLineSegment(
        mRID='B12-Tie5',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_4_s1
)[1].link_to(
    Switch(
        mRID='Tie6',
        normalOpen=True,
        open=True,
    ),
    feeder=feeder_4_s1
)

###
substation2 = Substation(mRID='JAB', name='Jabuti')
busbar_s2 = BusbarSection(mRID='JAB-busbar', EquipmentContainer=substation2)
transformer1_s2, transformer2_s2 = EquivalentInjection(
    mRID='EI2',
    BaseVoltage=base_voltage_1
).link_to(
    PowerTransformer(
        mRID='JAB-01T1',
        PowerTransformerEnd=[
            PowerTransformerEnd(
                endNumber=1,
                connectionKind='D',
                ratedS=ApparentPower('M', 'VA', '12.5'),
                ratedU=Voltage('k', 'V', '69'),
                r=Resistance('m', 'ohm', '10'),
                r0=Resistance('m', 'ohm', '10'),
                x=Reactance('m', 'ohm', '10'),
                x0=Reactance('m', 'ohm', '10'),
            ),
            PowerTransformerEnd(
                endNumber=2,
                connectionKind='D',
                ratedS=ApparentPower('M', 'VA', '12.5'),
                ratedU=Voltage('k', 'V', '13.8')
            )
        ],
        EquipmentContainer=substation2
    ),
    PowerTransformer(
        mRID='JAB-01T2',
        PowerTransformerEnd=[
            PowerTransformerEnd(
                endNumber=1,
                connectionKind='D',
                ratedS=ApparentPower('M', 'VA', '12.5'),
                ratedU=Voltage('k', 'V', '69'),
                r=Resistance('m', 'ohm', '10'),
                r0=Resistance('m', 'ohm', '10'),
                x=Reactance('m', 'ohm', '10'),
                x0=Reactance('m', 'ohm', '10'),
            ),
            PowerTransformerEnd(
                endNumber=2,
                connectionKind='D',
                ratedS=ApparentPower('M', 'VA', '12.5'),
                ratedU=Voltage('k', 'V', '13.8')
            )
        ],
        EquipmentContainer=substation2
    )
)
transformer1_s2.link_to(
    Switch(
        mRID='JAB-11T1',
        normalOpen=False,
        open=False
    )
).link_to(busbar_s2)
transformer2_s2.link_to(
    Switch(
        mRID='JAB-11T2',
        normalOpen=False,
        open=False
    )
).link_to(busbar_s2)
feeder_1_s2 = Feeder(mRID='JAB_01F8', FeedingSubstation=substation2)
busbar_s2.link_to(
    ACLineSegment(
        mRID='JAB-busbar-21F8',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_1_s2
).link_to(
    Switch(
        mRID='JAB-21F8',
        normalOpen=False,
        open=False,
    ),
    feeder=feeder_1_s2
).link_to(
    ACLineSegment(
        mRID='21F8-B3',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_1_s2
).link_to(
    EnergyConsumer(
        mRID='B3',
        p=ActivePower('M', 'W', '1.0'),
        q=ReactivePower('M', 'VAr', '0.1')
    ),
    ACLineSegment(
        mRID='B3-Tie3',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_1_s2
)[1].link_to(switch_tie3,
             feeder=feeder_1_s2)


###
substation3 = Substation(mRID='MSJ', name='Messejana')
busbar_s3 = BusbarSection(mRID='MSJ-busbar', EquipmentContainer=substation3)
EquivalentInjection(
    mRID='EI3',
    BaseVoltage=base_voltage_1
).link_to(
    PowerTransformer(
        mRID='MSJ-01T2',
        PowerTransformerEnd=[
            PowerTransformerEnd(
                endNumber=1,
                connectionKind='D',
                ratedS=ApparentPower('M', 'VA', '26.6'),
                ratedU=Voltage('k', 'V', '69'),
                r=Resistance('m', 'ohm', '10'),
                r0=Resistance('m', 'ohm', '10'),
                x=Reactance('m', 'ohm', '10'),
                x0=Reactance('m', 'ohm', '10'),
            ),
            PowerTransformerEnd(
                endNumber=2,
                connectionKind='D',
                ratedS=ApparentPower('M', 'VA', '26.6'),
                ratedU=Voltage('k', 'V', '13.8')
            )
        ],
        EquipmentContainer=substation3
    )
).link_to(
    Switch(
        mRID='MSJ-11T1',
        normalOpen=False,
        open=False
    )
).link_to(busbar_s3)
feeder_1_s3 = Feeder(mRID='MSJ_01L3', FeedingSubstation=substation3)
busbar_s3.link_to(
    ACLineSegment(
        mRID='MSJ-busbar_21M3',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_1_s3
).link_to(
    Switch(
        mRID='MSJ-21M3',
        normalOpen=False,
        open=False,
    ),
    feeder=feeder_1_s3
).link_to(
    ACLineSegment(
        mRID='21M3-B5',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_1_s3
).link_to(
    EnergyConsumer(
        mRID='B6',
        p=ActivePower('M', 'W', '1.0'),
        q=ReactivePower('M', 'VAr', '0.1')
    ),
    ACLineSegment(
        mRID='B6-Tie4',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_1_s3
)[1].link_to(switch_tie4,
             feeder=feeder_1_s3)


###
substation4 = Substation(mRID='AGF', name='Água Fria')
busbar_s4 = BusbarSection(mRID='AGF-busbar', EquipmentContainer=substation4)
transformer1_s4, transformer2_s4 = EquivalentInjection(
    mRID='EI4',
    BaseVoltage=base_voltage_1
).link_to(
    PowerTransformer(
        mRID='AGF-01T1',
        PowerTransformerEnd=[
            PowerTransformerEnd(
                endNumber=1,
                connectionKind='D',
                ratedS=ApparentPower('M', 'VA', '26.6'),
                ratedU=Voltage('k', 'V', '69'),
                r=Resistance('m', 'ohm', '10'),
                r0=Resistance('m', 'ohm', '10'),
                x=Reactance('m', 'ohm', '10'),
                x0=Reactance('m', 'ohm', '10'),
            ),
            PowerTransformerEnd(
                endNumber=2,
                connectionKind='D',
                ratedS=ApparentPower('M', 'VA', '26.6'),
                ratedU=Voltage('k', 'V', '13.8')
            )
        ],
        EquipmentContainer=substation4
    ),
    PowerTransformer(
        mRID='AGF-01T2',
        PowerTransformerEnd=[
            PowerTransformerEnd(
                endNumber=1,
                connectionKind='D',
                ratedS=ApparentPower('M', 'VA', '26.6'),
                ratedU=Voltage('k', 'V', '69'),
                r=Resistance('m', 'ohm', '10'),
                r0=Resistance('m', 'ohm', '10'),
                x=Reactance('m', 'ohm', '10'),
                x0=Reactance('m', 'ohm', '10'),
            ),
            PowerTransformerEnd(
                endNumber=2,
                connectionKind='D',
                ratedS=ApparentPower('M', 'VA', '26.6'),
                ratedU=Voltage('k', 'V', '13.8')
            )
        ],
        EquipmentContainer=substation4
    )
)
transformer1_s4.link_to(
    Switch(
        mRID='AGF-11T1',
        normalOpen=False,
        open=False
    )
).link_to(busbar_s4)
transformer2_s4.link_to(
    Switch(
        mRID='AGF-11T2',
        normalOpen=False,
        open=False
    )
).link_to(busbar_s4)
feeder_1_s4 = Feeder(mRID='AGF_01I7', FeedingSubstation=substation4)
B10, B10_tie5, B10_tie6 = busbar_s4.link_to(
    ACLineSegment(
        mRID='AGF_21I7',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_1_s4
).link_to(
    Switch(
        mRID='AGF-21I7',
        normalOpen=False,
        open=False,
    ),
    feeder=feeder_1_s4
).link_to(
    ACLineSegment(
        mRID='21I7-B10',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_1_s4
).link_to(
    EnergyConsumer(
        mRID='B10',
        p=ActivePower('M', 'W', '1.0'),
        q=ReactivePower('M', 'VAr', '0.1')
    ),
    ACLineSegment(
        mRID='B10-Tie5',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    ACLineSegment(
        mRID='B10-Tie6',
        PerLengthImpedance=conductor1_impedance,
        length=Length('k', 'm', '1.0'),
        OperationalLimitSet=[conductor1_limits],
    ),
    feeder=feeder_1_s4
)  # B10, B10_tie5, B10_tie6
B10_tie5.link_to(switch_tie5,
                 feeder=feeder_1_s4)
B10_tie6.link_to(switch_tie6,
                 feeder=feeder_1_s4)


doc = DocumentCIMRDF()
doc.add_recursively(substation1)
doc.tofile('rede/models/new-network.xml')
