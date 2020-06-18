from decimal import Decimal
from typing import List, Union
from uuid import uuid4 as uuid
from xml.etree import ElementTree as ET
from xml.dom.minidom import parseString

__RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
__RDFS_NS = "http://www.w3.org/2000/01/rdf-schema#"
__CIMS_NS = "http://iec.ch/TC57/1999/rdf-schema-extensions-19990926#"
__UML_NS = "http://langdale.com.au/2005/UML#"
__XSD_NS = "http://www.w3.org/2001/XMLSchema#"
__XML_NS = "http://www.w3.org/XML/1998/namespace"

__XML_BASE = '{'+__XML_NS+'}base'
__DESCRIPTION_TAG = '{'+__RDF_NS+'}Description'
__TYPE_TAG = '{'+__RDF_NS+'}type'
__LABEL_TAG = '{'+__RDFS_NS+'}label'
__COMMENT_TAG = '{'+__RDFS_NS+'}comment'
__RESOURCE_ATTRIB = '{'+__RDF_NS+'}resource'
__ABOUT_ATTRIB = '{'+__RDF_NS+'}about'
__STEREOTYPE_TAG = '{'+__CIMS_NS+'}stereotype'
# Class
__CLASS_TAG = '{'+__RDFS_NS+'}Class'
__CLASS_URI = __RDFS_NS+'Class'
__SUBCLASSOF_TAG = '{'+__RDFS_NS+'}subClassOf'
# Property
__PROPERTY_TAG = '{'+__RDF_NS+'}Property'
__PROPERTY_URI = __RDF_NS+'Property'
__DOMAIN_TAG = '{'+__RDFS_NS+'}domain'
__RANGE_TAG = '{'+__RDFS_NS+'}range'
__MULTIPLICITY_TAG = '{' + __CIMS_NS + '}multiplicity'
__INVERSEROLE_TAG = '{' + __CIMS_NS + '}inverseRoleName'
__DATATYPE_TAG = '{'+__CIMS_NS+'}dataType'
# Enumeration
__ENUMERATION_URI = __UML_NS+'enumeration'
# cim data type
__CIMDATATYPE_URI = __UML_NS+'cimdatatype'
__BASE_NS = 'grei.ufc.br/DistributionNetwork#'
def fromstring(xml):
    etree = ET.fromstring(xml)
    return __import(etree)
def fromfile(filename):
    etree = ET.parse(filename)
    return __import(etree)

def __import(etree):
    def get_type(element):
        if element.tag == __DESCRIPTION_TAG:
            return element.find(__TYPE_TAG).attrib[__RESOURCE_ATTRIB].split('#')[1]
        return element.tag.split('}')[1]
    def get_element_URI(element):
        try:
            return __BASE_NS.replace('#','') + '#' + element.attrib[__ID_ATTRIB]
        except:
            return __BASE_NS.replace('#','') + element.attrib[__ABOUT_ATTRIB]

    root = etree
    classes = {}

    try:
        __BASE_NS = root.attrib[__XML_BASE].replace('#', '') + '#'
    except:
        __BASE_NS = ''

    for child in root:
        new_class = get_type(child)
        uri = '#' + get_element_URI(child).split('#')[1]
        classes[uri] = eval(new_class + '()')
        classes[uri].URI = uri

    for child in root:
        uri = '#' + get_element_URI(child).split('#')[1]
        element = classes[uri]
        for attribute in child:
            dtype = get_type(attribute).replace('.', '_')
            if __RESOURCE_ATTRIB in attribute.attrib:
                resource_uri = attribute.attrib[__RESOURCE_ATTRIB]
                exec(f"""
if isinstance(element.{dtype}, list):
   element.add_{dtype}(classes[resource_uri])
else:
   element.{dtype} = classes[resource_uri]
""")
            else:
                value = attribute.text
                exec(f"""
if isinstance(element.{dtype}, list):
    element.add_{dtype}(value)
else:
    element.{dtype} = value
""")

    return classes
class DocumentCIMRDF():
    def __init__(self, resources = []):
        self.resources = []
        for resource in resources:
            self.resources.append(resource)

    def add_elements(self, elements: Union[ET.Element, List[ET.Element]]):
        elements = elements if isinstance(elements, list) else [elements]
        for element in elements:
            self.resources.append(element)

    def dump(self):
        etree = self.pack()
        rough_string = ET.tostring(etree, 'utf-8')
        reparsed = parseString(rough_string)
        print(reparsed.toprettyxml(indent=' '*4))
    
    def pack(self):
        root = ET.Element('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF', attrib={'{http://www.w3.org/XML/1998/namespace}base': 'grei.ufc.br/DistributionNetwork/new_resource#'})
        for element in self.resources:
            root.append(element.serialize())
        return root

    def tostring(self):
        return ET.tostring(self.pack())

class Enumeration:
    def __init__(self, value, allowed):
        if value not in allowed:
            raise ValueError(f'{value} is not in the Enumeration set')
        self.__value = value
    def __str__(self):
        return self.__value
    def __eq__(self, other):
        return self.__value == str(other)

class PhaseShuntConnectionKind(Enumeration):
    def __init__(self, value: str):
        self.__ALLOWED = ['D', 'Y', 'Yn']
        super().__init__(value, self.__ALLOWED)

class UnitMultiplier(Enumeration):
    def __init__(self, value: str):
        self.__ALLOWED = ['G', 'M', 'k', 'm', 'micro', 'none']
        super().__init__(value, self.__ALLOWED)

class UnitSymbol(Enumeration):
    def __init__(self, value: str):
        self.__ALLOWED = ['S', 'VAr', 'W', 'm', 'none', 'ohm']
        super().__init__(value, self.__ALLOWED)

class WindingConnection(Enumeration):
    def __init__(self, value: str):
        self.__ALLOWED = ['D', 'Y', 'Yn', 'Z', 'Zn']
        super().__init__(value, self.__ALLOWED)
 
class ActivePower():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__ActivePower_multiplier: 'UnitMultiplier' = None
        self.__ActivePower_unit: 'UnitSymbol' = None
        self.__ActivePower_value: Decimal = None
    @property
    def ActivePower_multiplier(self) -> 'UnitMultiplier':
        return self.__ActivePower_multiplier
    @ActivePower_multiplier.setter
    def ActivePower_multiplier(self, value: 'UnitMultiplier'):
        if self.__ActivePower_multiplier == None:
            self.__ActivePower_multiplier = value
    @property
    def ActivePower_unit(self) -> 'UnitSymbol':
        return self.__ActivePower_unit
    @ActivePower_unit.setter
    def ActivePower_unit(self, value: 'UnitSymbol'):
        if self.__ActivePower_unit == None:
            self.__ActivePower_unit = value
    @property
    def ActivePower_value(self) -> Decimal:
        return self.__ActivePower_value
    @ActivePower_value.setter
    def ActivePower_value(self, value: Decimal):
        if self.__ActivePower_value == None:
            self.__ActivePower_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}ActivePower', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__ActivePower_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ActivePower.multiplier')
            prop.text = str(self.__ActivePower_multiplier)
        if self.__ActivePower_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ActivePower.unit')
            prop.text = str(self.__ActivePower_unit)
        if self.__ActivePower_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ActivePower.value')
            prop.text = str(self.__ActivePower_value)
        return root
    
    def validate(self):
        
        if not isinstance(self.ActivePower_multiplier, UnitMultiplier) and self.ActivePower_multiplier != None:
            raise ValueError('Incorrect datatype in ActivePower_multiplier')
        if not isinstance(self.ActivePower_unit, UnitSymbol) and self.ActivePower_unit != None:
            raise ValueError('Incorrect datatype in ActivePower_unit')
        if not isinstance(self.ActivePower_value, Decimal):
            raise ValueError('Incorrect datatype in ActivePower_value')
 
class ApparentPower():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__ApparentPower_multiplier: 'UnitMultiplier' = None
        self.__ApparentPower_unit: 'UnitSymbol' = None
        self.__ApparentPower_value: Decimal = None
    @property
    def ApparentPower_multiplier(self) -> 'UnitMultiplier':
        return self.__ApparentPower_multiplier
    @ApparentPower_multiplier.setter
    def ApparentPower_multiplier(self, value: 'UnitMultiplier'):
        if self.__ApparentPower_multiplier == None:
            self.__ApparentPower_multiplier = value
    @property
    def ApparentPower_unit(self) -> 'UnitSymbol':
        return self.__ApparentPower_unit
    @ApparentPower_unit.setter
    def ApparentPower_unit(self, value: 'UnitSymbol'):
        if self.__ApparentPower_unit == None:
            self.__ApparentPower_unit = value
    @property
    def ApparentPower_value(self) -> Decimal:
        return self.__ApparentPower_value
    @ApparentPower_value.setter
    def ApparentPower_value(self, value: Decimal):
        if self.__ApparentPower_value == None:
            self.__ApparentPower_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}ApparentPower', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__ApparentPower_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ApparentPower.multiplier')
            prop.text = str(self.__ApparentPower_multiplier)
        if self.__ApparentPower_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ApparentPower.unit')
            prop.text = str(self.__ApparentPower_unit)
        if self.__ApparentPower_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ApparentPower.value')
            prop.text = str(self.__ApparentPower_value)
        return root
    
    def validate(self):
        
        if not isinstance(self.ApparentPower_multiplier, UnitMultiplier) and self.ApparentPower_multiplier != None:
            raise ValueError('Incorrect datatype in ApparentPower_multiplier')
        if not isinstance(self.ApparentPower_unit, UnitSymbol) and self.ApparentPower_unit != None:
            raise ValueError('Incorrect datatype in ApparentPower_unit')
        if not isinstance(self.ApparentPower_value, Decimal):
            raise ValueError('Incorrect datatype in ApparentPower_value')
 
class BaseVoltage():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__BaseVoltage_ConductingEquipment: List['EquivalentInjection'] = []
        self.__BaseVoltage_nominalVoltage: 'Voltage' = None
    def add_BaseVoltage_ConductingEquipment(self, value: 'EquivalentInjection'):
        if value not in self.__BaseVoltage_ConductingEquipment:
            self.__BaseVoltage_ConductingEquipment.append(value)
            if isinstance(value.EquivalentInjection_BaseVoltage, list):
                value.add_EquivalentInjection_BaseVoltage(self)
            else:
                value.EquivalentInjection_BaseVoltage = self
    @property
    def BaseVoltage_ConductingEquipment(self) -> List['EquivalentInjection']:
        return self.__BaseVoltage_ConductingEquipment
    @BaseVoltage_ConductingEquipment.setter
    def BaseVoltage_ConductingEquipment(self, list_objs: List['EquivalentInjection']):
        if self.__BaseVoltage_ConductingEquipment == []:
            self.__BaseVoltage_ConductingEquipment = list_objs
            if isinstance(list_objs[0].EquivalentInjection_BaseVoltage, list):
                for obj in list_objs:
                    obj.add_EquivalentInjection_BaseVoltage(self)
            else:
                for obj in list_objs:
                    obj.EquivalentInjection_BaseVoltage = self
    @property
    def BaseVoltage_nominalVoltage(self) -> 'Voltage':
        return self.__BaseVoltage_nominalVoltage
    @BaseVoltage_nominalVoltage.setter
    def BaseVoltage_nominalVoltage(self, value: 'Voltage'):
        if self.__BaseVoltage_nominalVoltage == None:
            self.__BaseVoltage_nominalVoltage = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}BaseVoltage', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__BaseVoltage_ConductingEquipment != []:
            for item in self.__BaseVoltage_ConductingEquipment:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}BaseVoltage.ConductingEquipment', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        if self.__BaseVoltage_nominalVoltage != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}BaseVoltage.nominalVoltage', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__BaseVoltage_nominalVoltage.URI})
        return root
    
    def validate(self):
        
        minBound, maxBound = 0, float('Inf')
        if len(self.BaseVoltage_ConductingEquipment) < minBound or len(self.BaseVoltage_ConductingEquipment) > maxBound:
            raise ValueError('Incorrect multiplicity in BaseVoltage_ConductingEquipment')
        if any(not isinstance(item, EquivalentInjection) for item in self.BaseVoltage_ConductingEquipment):
            raise ValueError('Incorrect datatype in BaseVoltage_ConductingEquipment')
        if not isinstance(self.BaseVoltage_nominalVoltage, Voltage):
            raise ValueError('Incorrect datatype in BaseVoltage_nominalVoltage')
 
class Conductance():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__Conductance_multiplier: 'UnitMultiplier' = None
        self.__Conductance_unit: 'UnitSymbol' = None
        self.__Conductance_value: Decimal = None
    @property
    def Conductance_multiplier(self) -> 'UnitMultiplier':
        return self.__Conductance_multiplier
    @Conductance_multiplier.setter
    def Conductance_multiplier(self, value: 'UnitMultiplier'):
        if self.__Conductance_multiplier == None:
            self.__Conductance_multiplier = value
    @property
    def Conductance_unit(self) -> 'UnitSymbol':
        return self.__Conductance_unit
    @Conductance_unit.setter
    def Conductance_unit(self, value: 'UnitSymbol'):
        if self.__Conductance_unit == None:
            self.__Conductance_unit = value
    @property
    def Conductance_value(self) -> Decimal:
        return self.__Conductance_value
    @Conductance_value.setter
    def Conductance_value(self, value: Decimal):
        if self.__Conductance_value == None:
            self.__Conductance_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Conductance', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__Conductance_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Conductance.multiplier')
            prop.text = str(self.__Conductance_multiplier)
        if self.__Conductance_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Conductance.unit')
            prop.text = str(self.__Conductance_unit)
        if self.__Conductance_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Conductance.value')
            prop.text = str(self.__Conductance_value)
        return root
    
    def validate(self):
        
        if not isinstance(self.Conductance_multiplier, UnitMultiplier) and self.Conductance_multiplier != None:
            raise ValueError('Incorrect datatype in Conductance_multiplier')
        if not isinstance(self.Conductance_unit, UnitSymbol) and self.Conductance_unit != None:
            raise ValueError('Incorrect datatype in Conductance_unit')
        if not isinstance(self.Conductance_value, Decimal):
            raise ValueError('Incorrect datatype in Conductance_value')
 
class ConnectivityNode():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__ConnectivityNode_Terminals: List['Terminal'] = []
        self.__ConnectivityNode_mRID: str = None
    def add_ConnectivityNode_Terminals(self, value: 'Terminal'):
        if value not in self.__ConnectivityNode_Terminals:
            self.__ConnectivityNode_Terminals.append(value)
            if isinstance(value.Terminal_ConnectivityNode, list):
                value.add_Terminal_ConnectivityNode(self)
            else:
                value.Terminal_ConnectivityNode = self
    @property
    def ConnectivityNode_Terminals(self) -> List['Terminal']:
        return self.__ConnectivityNode_Terminals
    @ConnectivityNode_Terminals.setter
    def ConnectivityNode_Terminals(self, list_objs: List['Terminal']):
        if self.__ConnectivityNode_Terminals == []:
            self.__ConnectivityNode_Terminals = list_objs
            if isinstance(list_objs[0].Terminal_ConnectivityNode, list):
                for obj in list_objs:
                    obj.add_Terminal_ConnectivityNode(self)
            else:
                for obj in list_objs:
                    obj.Terminal_ConnectivityNode = self
    @property
    def ConnectivityNode_mRID(self) -> str:
        return self.__ConnectivityNode_mRID
    @ConnectivityNode_mRID.setter
    def ConnectivityNode_mRID(self, value: str):
        if self.__ConnectivityNode_mRID == None:
            self.__ConnectivityNode_mRID = str(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}ConnectivityNode', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__ConnectivityNode_Terminals != []:
            for item in self.__ConnectivityNode_Terminals:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ConnectivityNode.Terminals', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        if self.__ConnectivityNode_mRID != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ConnectivityNode.mRID')
            prop.text = str(self.__ConnectivityNode_mRID)
        return root
    
    def validate(self):
        
        minBound, maxBound = 0, float('Inf')
        if len(self.ConnectivityNode_Terminals) < minBound or len(self.ConnectivityNode_Terminals) > maxBound:
            raise ValueError('Incorrect multiplicity in ConnectivityNode_Terminals')
        if any(not isinstance(item, Terminal) for item in self.ConnectivityNode_Terminals):
            raise ValueError('Incorrect datatype in ConnectivityNode_Terminals')
        if not isinstance(self.ConnectivityNode_mRID, str):
            raise ValueError('Incorrect datatype in ConnectivityNode_mRID')
 
class Equipment():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__Equipment_EquipmentContainer: 'Feeder' = None
    @property
    def Equipment_EquipmentContainer(self) -> 'Feeder':
        return self.__Equipment_EquipmentContainer
    @Equipment_EquipmentContainer.setter
    def Equipment_EquipmentContainer(self, value: 'Feeder'):
        if self.__Equipment_EquipmentContainer == None:
            self.__Equipment_EquipmentContainer = value
            if isinstance(value.Feeder_Equipments, list):
                value.add_Feeder_Equipments(self)
            else:
                value.Feeder_Equipments = self
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Equipment', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__Equipment_EquipmentContainer != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Equipment.EquipmentContainer', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__Equipment_EquipmentContainer.URI})
        return root
    
    def validate(self):
        
        if not isinstance(self.Equipment_EquipmentContainer, Feeder) and self.Equipment_EquipmentContainer != None:
            raise ValueError('Incorrect datatype in Equipment_EquipmentContainer')
 
class EquivalentInjection(Equipment):
    def __init__(self):
        super().__init__()
        self.__EquivalentInjection_BaseVoltage: 'BaseVoltage' = None
        self.__EquivalentInjection_Terminals: 'Terminal' = None
        self.__EquivalentInjection_mRID: str = None
        self.__EquivalentInjection_r: 'Resistance' = None
        self.__EquivalentInjection_r0: 'Resistance' = None
        self.__EquivalentInjection_x: 'Reactance' = None
        self.__EquivalentInjection_x0: 'Reactance' = None
    @property
    def EquivalentInjection_BaseVoltage(self) -> 'BaseVoltage':
        return self.__EquivalentInjection_BaseVoltage
    @EquivalentInjection_BaseVoltage.setter
    def EquivalentInjection_BaseVoltage(self, value: 'BaseVoltage'):
        if self.__EquivalentInjection_BaseVoltage == None:
            self.__EquivalentInjection_BaseVoltage = value
            if isinstance(value.BaseVoltage_ConductingEquipment, list):
                value.add_BaseVoltage_ConductingEquipment(self)
            else:
                value.BaseVoltage_ConductingEquipment = self
    @property
    def EquivalentInjection_Terminals(self) -> 'Terminal':
        return self.__EquivalentInjection_Terminals
    @EquivalentInjection_Terminals.setter
    def EquivalentInjection_Terminals(self, value: 'Terminal'):
        if self.__EquivalentInjection_Terminals == None:
            self.__EquivalentInjection_Terminals = value
    @property
    def EquivalentInjection_mRID(self) -> str:
        return self.__EquivalentInjection_mRID
    @EquivalentInjection_mRID.setter
    def EquivalentInjection_mRID(self, value: str):
        if self.__EquivalentInjection_mRID == None:
            self.__EquivalentInjection_mRID = str(value)
    @property
    def EquivalentInjection_r(self) -> 'Resistance':
        return self.__EquivalentInjection_r
    @EquivalentInjection_r.setter
    def EquivalentInjection_r(self, value: 'Resistance'):
        if self.__EquivalentInjection_r == None:
            self.__EquivalentInjection_r = value
    @property
    def EquivalentInjection_r0(self) -> 'Resistance':
        return self.__EquivalentInjection_r0
    @EquivalentInjection_r0.setter
    def EquivalentInjection_r0(self, value: 'Resistance'):
        if self.__EquivalentInjection_r0 == None:
            self.__EquivalentInjection_r0 = value
    @property
    def EquivalentInjection_x(self) -> 'Reactance':
        return self.__EquivalentInjection_x
    @EquivalentInjection_x.setter
    def EquivalentInjection_x(self, value: 'Reactance'):
        if self.__EquivalentInjection_x == None:
            self.__EquivalentInjection_x = value
    @property
    def EquivalentInjection_x0(self) -> 'Reactance':
        return self.__EquivalentInjection_x0
    @EquivalentInjection_x0.setter
    def EquivalentInjection_x0(self, value: 'Reactance'):
        if self.__EquivalentInjection_x0 == None:
            self.__EquivalentInjection_x0 = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}EquivalentInjection' 
        if self.__EquivalentInjection_BaseVoltage != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EquivalentInjection.BaseVoltage', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__EquivalentInjection_BaseVoltage.URI})
        if self.__EquivalentInjection_Terminals != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EquivalentInjection.Terminals', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__EquivalentInjection_Terminals.URI})
        if self.__EquivalentInjection_mRID != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EquivalentInjection.mRID')
            prop.text = str(self.__EquivalentInjection_mRID)
        if self.__EquivalentInjection_r != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EquivalentInjection.r', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__EquivalentInjection_r.URI})
        if self.__EquivalentInjection_r0 != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EquivalentInjection.r0', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__EquivalentInjection_r0.URI})
        if self.__EquivalentInjection_x != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EquivalentInjection.x', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__EquivalentInjection_x.URI})
        if self.__EquivalentInjection_x0 != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EquivalentInjection.x0', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__EquivalentInjection_x0.URI})
        return root
    
    def validate(self):
        super().validate()
        if not isinstance(self.EquivalentInjection_BaseVoltage, BaseVoltage) and self.EquivalentInjection_BaseVoltage != None:
            raise ValueError('Incorrect datatype in EquivalentInjection_BaseVoltage')
        if not isinstance(self.EquivalentInjection_Terminals, Terminal):
            raise ValueError('Incorrect datatype in EquivalentInjection_Terminals')
        if not isinstance(self.EquivalentInjection_mRID, str):
            raise ValueError('Incorrect datatype in EquivalentInjection_mRID')
        if not isinstance(self.EquivalentInjection_r, Resistance) and self.EquivalentInjection_r != None:
            raise ValueError('Incorrect datatype in EquivalentInjection_r')
        if not isinstance(self.EquivalentInjection_r0, Resistance) and self.EquivalentInjection_r0 != None:
            raise ValueError('Incorrect datatype in EquivalentInjection_r0')
        if not isinstance(self.EquivalentInjection_x, Reactance) and self.EquivalentInjection_x != None:
            raise ValueError('Incorrect datatype in EquivalentInjection_x')
        if not isinstance(self.EquivalentInjection_x0, Reactance) and self.EquivalentInjection_x0 != None:
            raise ValueError('Incorrect datatype in EquivalentInjection_x0')
 
class Feeder():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__Feeder_Equipments: List['Equipment'] = []
        self.__Feeder_FeedingSubstation: 'Substation' = None
        self.__Feeder_mRID: str = None
    def add_Feeder_Equipments(self, value: 'Equipment'):
        if value not in self.__Feeder_Equipments:
            self.__Feeder_Equipments.append(value)
            if isinstance(value.Equipment_EquipmentContainer, list):
                value.add_Equipment_EquipmentContainer(self)
            else:
                value.Equipment_EquipmentContainer = self
    @property
    def Feeder_Equipments(self) -> List['Equipment']:
        return self.__Feeder_Equipments
    @Feeder_Equipments.setter
    def Feeder_Equipments(self, list_objs: List['Equipment']):
        if self.__Feeder_Equipments == []:
            self.__Feeder_Equipments = list_objs
            if isinstance(list_objs[0].Equipment_EquipmentContainer, list):
                for obj in list_objs:
                    obj.add_Equipment_EquipmentContainer(self)
            else:
                for obj in list_objs:
                    obj.Equipment_EquipmentContainer = self
    @property
    def Feeder_FeedingSubstation(self) -> 'Substation':
        return self.__Feeder_FeedingSubstation
    @Feeder_FeedingSubstation.setter
    def Feeder_FeedingSubstation(self, value: 'Substation'):
        if self.__Feeder_FeedingSubstation == None:
            self.__Feeder_FeedingSubstation = value
            if isinstance(value.Substation_SubstationFeeder, list):
                value.add_Substation_SubstationFeeder(self)
            else:
                value.Substation_SubstationFeeder = self
    @property
    def Feeder_mRID(self) -> str:
        return self.__Feeder_mRID
    @Feeder_mRID.setter
    def Feeder_mRID(self, value: str):
        if self.__Feeder_mRID == None:
            self.__Feeder_mRID = str(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Feeder', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__Feeder_Equipments != []:
            for item in self.__Feeder_Equipments:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Feeder.Equipments', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        if self.__Feeder_FeedingSubstation != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Feeder.FeedingSubstation', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__Feeder_FeedingSubstation.URI})
        if self.__Feeder_mRID != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Feeder.mRID')
            prop.text = str(self.__Feeder_mRID)
        return root
    
    def validate(self):
        
        minBound, maxBound = 0, float('Inf')
        if len(self.Feeder_Equipments) < minBound or len(self.Feeder_Equipments) > maxBound:
            raise ValueError('Incorrect multiplicity in Feeder_Equipments')
        if any(not isinstance(item, Equipment) for item in self.Feeder_Equipments):
            raise ValueError('Incorrect datatype in Feeder_Equipments')
        if not isinstance(self.Feeder_FeedingSubstation, Substation):
            raise ValueError('Incorrect datatype in Feeder_FeedingSubstation')
        if not isinstance(self.Feeder_mRID, str):
            raise ValueError('Incorrect datatype in Feeder_mRID')
 
class Length():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__Length_multiplier: 'UnitMultiplier' = None
        self.__Length_unit: 'UnitSymbol' = None
        self.__Length_value: Decimal = None
    @property
    def Length_multiplier(self) -> 'UnitMultiplier':
        return self.__Length_multiplier
    @Length_multiplier.setter
    def Length_multiplier(self, value: 'UnitMultiplier'):
        if self.__Length_multiplier == None:
            self.__Length_multiplier = value
    @property
    def Length_unit(self) -> 'UnitSymbol':
        return self.__Length_unit
    @Length_unit.setter
    def Length_unit(self, value: 'UnitSymbol'):
        if self.__Length_unit == None:
            self.__Length_unit = value
    @property
    def Length_value(self) -> Decimal:
        return self.__Length_value
    @Length_value.setter
    def Length_value(self, value: Decimal):
        if self.__Length_value == None:
            self.__Length_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Length', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__Length_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Length.multiplier')
            prop.text = str(self.__Length_multiplier)
        if self.__Length_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Length.unit')
            prop.text = str(self.__Length_unit)
        if self.__Length_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Length.value')
            prop.text = str(self.__Length_value)
        return root
    
    def validate(self):
        
        if not isinstance(self.Length_multiplier, UnitMultiplier) and self.Length_multiplier != None:
            raise ValueError('Incorrect datatype in Length_multiplier')
        if not isinstance(self.Length_unit, UnitSymbol) and self.Length_unit != None:
            raise ValueError('Incorrect datatype in Length_unit')
        if not isinstance(self.Length_value, Decimal):
            raise ValueError('Incorrect datatype in Length_value')
 
class Line():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__Line_Equipments: List['Equipment'] = []
        self.__Line_mRID: str = None
    def add_Line_Equipments(self, value: 'Equipment'):
        if value not in self.__Line_Equipments:
            self.__Line_Equipments.append(value)
    @property
    def Line_Equipments(self) -> List['Equipment']:
        return self.__Line_Equipments
    @Line_Equipments.setter
    def Line_Equipments(self, list_objs: List['Equipment']):
        if self.__Line_Equipments == []:
            self.__Line_Equipments = list_objs
    @property
    def Line_mRID(self) -> str:
        return self.__Line_mRID
    @Line_mRID.setter
    def Line_mRID(self, value: str):
        if self.__Line_mRID == None:
            self.__Line_mRID = str(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Line', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__Line_Equipments != []:
            for item in self.__Line_Equipments:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Line.Equipments', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        if self.__Line_mRID != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Line.mRID')
            prop.text = str(self.__Line_mRID)
        return root
    
    def validate(self):
        
        minBound, maxBound = 0, float('Inf')
        if len(self.Line_Equipments) < minBound or len(self.Line_Equipments) > maxBound:
            raise ValueError('Incorrect multiplicity in Line_Equipments')
        if any(not isinstance(item, Equipment) for item in self.Line_Equipments):
            raise ValueError('Incorrect datatype in Line_Equipments')
        if not isinstance(self.Line_mRID, str) and self.Line_mRID != None:
            raise ValueError('Incorrect datatype in Line_mRID')
 
class PowerTransformer(Equipment):
    def __init__(self):
        super().__init__()
        self.__PowerTransformer_PowerTransformerEnd: List['PowerTransformerEnd'] = []
        self.__PowerTransformer_mRID: str = None
    def add_PowerTransformer_PowerTransformerEnd(self, value: 'PowerTransformerEnd'):
        if value not in self.__PowerTransformer_PowerTransformerEnd:
            self.__PowerTransformer_PowerTransformerEnd.append(value)
    @property
    def PowerTransformer_PowerTransformerEnd(self) -> List['PowerTransformerEnd']:
        return self.__PowerTransformer_PowerTransformerEnd
    @PowerTransformer_PowerTransformerEnd.setter
    def PowerTransformer_PowerTransformerEnd(self, list_objs: List['PowerTransformerEnd']):
        if self.__PowerTransformer_PowerTransformerEnd == []:
            self.__PowerTransformer_PowerTransformerEnd = list_objs
    @property
    def PowerTransformer_mRID(self) -> str:
        return self.__PowerTransformer_mRID
    @PowerTransformer_mRID.setter
    def PowerTransformer_mRID(self, value: str):
        if self.__PowerTransformer_mRID == None:
            self.__PowerTransformer_mRID = str(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}PowerTransformer' 
        if self.__PowerTransformer_PowerTransformerEnd != []:
            for item in self.__PowerTransformer_PowerTransformerEnd:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformer.PowerTransformerEnd', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        if self.__PowerTransformer_mRID != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformer.mRID')
            prop.text = str(self.__PowerTransformer_mRID)
        return root
    
    def validate(self):
        super().validate()
        minBound, maxBound = 0, float('Inf')
        if len(self.PowerTransformer_PowerTransformerEnd) < minBound or len(self.PowerTransformer_PowerTransformerEnd) > maxBound:
            raise ValueError('Incorrect multiplicity in PowerTransformer_PowerTransformerEnd')
        if any(not isinstance(item, PowerTransformerEnd) for item in self.PowerTransformer_PowerTransformerEnd):
            raise ValueError('Incorrect datatype in PowerTransformer_PowerTransformerEnd')
        if not isinstance(self.PowerTransformer_mRID, str) and self.PowerTransformer_mRID != None:
            raise ValueError('Incorrect datatype in PowerTransformer_mRID')
 
class PowerTransformerEnd():
    def __init__(self):
        self.URI = '#' + str(uuid())
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        return root
    
    def validate(self):
        
 
class Reactance():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__Reactance_multiplier: 'UnitMultiplier' = None
        self.__Reactance_unit: 'UnitSymbol' = None
        self.__Reactance_value: Decimal = None
    @property
    def Reactance_multiplier(self) -> 'UnitMultiplier':
        return self.__Reactance_multiplier
    @Reactance_multiplier.setter
    def Reactance_multiplier(self, value: 'UnitMultiplier'):
        if self.__Reactance_multiplier == None:
            self.__Reactance_multiplier = value
    @property
    def Reactance_unit(self) -> 'UnitSymbol':
        return self.__Reactance_unit
    @Reactance_unit.setter
    def Reactance_unit(self, value: 'UnitSymbol'):
        if self.__Reactance_unit == None:
            self.__Reactance_unit = value
    @property
    def Reactance_value(self) -> Decimal:
        return self.__Reactance_value
    @Reactance_value.setter
    def Reactance_value(self, value: Decimal):
        if self.__Reactance_value == None:
            self.__Reactance_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Reactance', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__Reactance_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Reactance.multiplier')
            prop.text = str(self.__Reactance_multiplier)
        if self.__Reactance_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Reactance.unit')
            prop.text = str(self.__Reactance_unit)
        if self.__Reactance_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Reactance.value')
            prop.text = str(self.__Reactance_value)
        return root
    
    def validate(self):
        
        if not isinstance(self.Reactance_multiplier, UnitMultiplier) and self.Reactance_multiplier != None:
            raise ValueError('Incorrect datatype in Reactance_multiplier')
        if not isinstance(self.Reactance_unit, UnitSymbol) and self.Reactance_unit != None:
            raise ValueError('Incorrect datatype in Reactance_unit')
        if not isinstance(self.Reactance_value, Decimal):
            raise ValueError('Incorrect datatype in Reactance_value')
 
class ReactivePower():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__ReactivePower_multiplier: 'UnitMultiplier' = None
        self.__ReactivePower_unit: 'UnitSymbol' = None
        self.__ReactivePower_value: Decimal = None
    @property
    def ReactivePower_multiplier(self) -> 'UnitMultiplier':
        return self.__ReactivePower_multiplier
    @ReactivePower_multiplier.setter
    def ReactivePower_multiplier(self, value: 'UnitMultiplier'):
        if self.__ReactivePower_multiplier == None:
            self.__ReactivePower_multiplier = value
    @property
    def ReactivePower_unit(self) -> 'UnitSymbol':
        return self.__ReactivePower_unit
    @ReactivePower_unit.setter
    def ReactivePower_unit(self, value: 'UnitSymbol'):
        if self.__ReactivePower_unit == None:
            self.__ReactivePower_unit = value
    @property
    def ReactivePower_value(self) -> Decimal:
        return self.__ReactivePower_value
    @ReactivePower_value.setter
    def ReactivePower_value(self, value: Decimal):
        if self.__ReactivePower_value == None:
            self.__ReactivePower_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}ReactivePower', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__ReactivePower_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ReactivePower.multiplier')
            prop.text = str(self.__ReactivePower_multiplier)
        if self.__ReactivePower_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ReactivePower.unit')
            prop.text = str(self.__ReactivePower_unit)
        if self.__ReactivePower_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ReactivePower.value')
            prop.text = str(self.__ReactivePower_value)
        return root
    
    def validate(self):
        
        if not isinstance(self.ReactivePower_multiplier, UnitMultiplier) and self.ReactivePower_multiplier != None:
            raise ValueError('Incorrect datatype in ReactivePower_multiplier')
        if not isinstance(self.ReactivePower_unit, UnitSymbol) and self.ReactivePower_unit != None:
            raise ValueError('Incorrect datatype in ReactivePower_unit')
        if not isinstance(self.ReactivePower_value, Decimal):
            raise ValueError('Incorrect datatype in ReactivePower_value')
 
class Resistance():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__Resistance_multiplier: 'UnitMultiplier' = None
        self.__Resistance_unit: 'UnitSymbol' = None
        self.__Resistance_value: Decimal = None
    @property
    def Resistance_multiplier(self) -> 'UnitMultiplier':
        return self.__Resistance_multiplier
    @Resistance_multiplier.setter
    def Resistance_multiplier(self, value: 'UnitMultiplier'):
        if self.__Resistance_multiplier == None:
            self.__Resistance_multiplier = value
    @property
    def Resistance_unit(self) -> 'UnitSymbol':
        return self.__Resistance_unit
    @Resistance_unit.setter
    def Resistance_unit(self, value: 'UnitSymbol'):
        if self.__Resistance_unit == None:
            self.__Resistance_unit = value
    @property
    def Resistance_value(self) -> Decimal:
        return self.__Resistance_value
    @Resistance_value.setter
    def Resistance_value(self, value: Decimal):
        if self.__Resistance_value == None:
            self.__Resistance_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Resistance', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__Resistance_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Resistance.multiplier')
            prop.text = str(self.__Resistance_multiplier)
        if self.__Resistance_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Resistance.unit')
            prop.text = str(self.__Resistance_unit)
        if self.__Resistance_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Resistance.value')
            prop.text = str(self.__Resistance_value)
        return root
    
    def validate(self):
        
        if not isinstance(self.Resistance_multiplier, UnitMultiplier) and self.Resistance_multiplier != None:
            raise ValueError('Incorrect datatype in Resistance_multiplier')
        if not isinstance(self.Resistance_unit, UnitSymbol) and self.Resistance_unit != None:
            raise ValueError('Incorrect datatype in Resistance_unit')
        if not isinstance(self.Resistance_value, Decimal):
            raise ValueError('Incorrect datatype in Resistance_value')
 
class Substation():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__Substation_SubstationFeeder: List['Feeder'] = []
        self.__Substation_mRID: str = None
    def add_Substation_SubstationFeeder(self, value: 'Feeder'):
        if value not in self.__Substation_SubstationFeeder:
            self.__Substation_SubstationFeeder.append(value)
            if isinstance(value.Feeder_FeedingSubstation, list):
                value.add_Feeder_FeedingSubstation(self)
            else:
                value.Feeder_FeedingSubstation = self
    @property
    def Substation_SubstationFeeder(self) -> List['Feeder']:
        return self.__Substation_SubstationFeeder
    @Substation_SubstationFeeder.setter
    def Substation_SubstationFeeder(self, list_objs: List['Feeder']):
        if self.__Substation_SubstationFeeder == []:
            self.__Substation_SubstationFeeder = list_objs
            if isinstance(list_objs[0].Feeder_FeedingSubstation, list):
                for obj in list_objs:
                    obj.add_Feeder_FeedingSubstation(self)
            else:
                for obj in list_objs:
                    obj.Feeder_FeedingSubstation = self
    @property
    def Substation_mRID(self) -> str:
        return self.__Substation_mRID
    @Substation_mRID.setter
    def Substation_mRID(self, value: str):
        if self.__Substation_mRID == None:
            self.__Substation_mRID = str(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Substation', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__Substation_SubstationFeeder != []:
            for item in self.__Substation_SubstationFeeder:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Substation.SubstationFeeder', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        if self.__Substation_mRID != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Substation.mRID')
            prop.text = str(self.__Substation_mRID)
        return root
    
    def validate(self):
        
        minBound, maxBound = 0, float('Inf')
        if len(self.Substation_SubstationFeeder) < minBound or len(self.Substation_SubstationFeeder) > maxBound:
            raise ValueError('Incorrect multiplicity in Substation_SubstationFeeder')
        if any(not isinstance(item, Feeder) for item in self.Substation_SubstationFeeder):
            raise ValueError('Incorrect datatype in Substation_SubstationFeeder')
        if not isinstance(self.Substation_mRID, str):
            raise ValueError('Incorrect datatype in Substation_mRID')
 
class Susceptance():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__Susceptance_multiplier: 'UnitMultiplier' = None
        self.__Susceptance_unit: 'UnitSymbol' = None
        self.__Susceptance_value: List[Decimal] = []
    @property
    def Susceptance_multiplier(self) -> 'UnitMultiplier':
        return self.__Susceptance_multiplier
    @Susceptance_multiplier.setter
    def Susceptance_multiplier(self, value: 'UnitMultiplier'):
        if self.__Susceptance_multiplier == None:
            self.__Susceptance_multiplier = value
    @property
    def Susceptance_unit(self) -> 'UnitSymbol':
        return self.__Susceptance_unit
    @Susceptance_unit.setter
    def Susceptance_unit(self, value: 'UnitSymbol'):
        if self.__Susceptance_unit == None:
            self.__Susceptance_unit = value
    def add_Susceptance_value(self, value: Decimal):
        if value not in self.__Susceptance_value:
            self.__Susceptance_value.append(value)
    @property
    def Susceptance_value(self) -> List[Decimal]:
        return self.__Susceptance_value
    @Susceptance_value.setter
    def Susceptance_value(self, list_objs: List[Decimal]):
        if self.__Susceptance_value == []:
            self.__Susceptance_value = list_objs
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Susceptance', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__Susceptance_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Susceptance.multiplier')
            prop.text = str(self.__Susceptance_multiplier)
        if self.__Susceptance_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Susceptance.unit')
            prop.text = str(self.__Susceptance_unit)
        if self.__Susceptance_value != []:
            for item in self.__Susceptance_value:
                prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Susceptance.value')
                prop.text = str(item)
        return root
    
    def validate(self):
        
        if not isinstance(self.Susceptance_multiplier, UnitMultiplier) and self.Susceptance_multiplier != None:
            raise ValueError('Incorrect datatype in Susceptance_multiplier')
        if not isinstance(self.Susceptance_unit, UnitSymbol) and self.Susceptance_unit != None:
            raise ValueError('Incorrect datatype in Susceptance_unit')
        minBound, maxBound = 1, float('Inf')
        if len(self.Susceptance_value) < minBound or len(self.Susceptance_value) > maxBound:
            raise ValueError('Incorrect multiplicity in Susceptance_value')
        if any(not isinstance(item, Decimal) for item in self.Susceptance_value):
            raise ValueError('Incorrect datatype in Susceptance_value')
 
class Switch(Equipment):
    def __init__(self):
        super().__init__()
        self.__Switch_Terminals: List['Terminal'] = []
        self.__Switch_mRID: str = None
        self.__Switch_normalOpen: bool = None
        self.__Switch_open: bool = None
    def add_Switch_Terminals(self, value: 'Terminal'):
        if value not in self.__Switch_Terminals:
            self.__Switch_Terminals.append(value)
    @property
    def Switch_Terminals(self) -> List['Terminal']:
        return self.__Switch_Terminals
    @Switch_Terminals.setter
    def Switch_Terminals(self, list_objs: List['Terminal']):
        if self.__Switch_Terminals == []:
            self.__Switch_Terminals = list_objs
    @property
    def Switch_mRID(self) -> str:
        return self.__Switch_mRID
    @Switch_mRID.setter
    def Switch_mRID(self, value: str):
        if self.__Switch_mRID == None:
            self.__Switch_mRID = str(value)
    @property
    def Switch_normalOpen(self) -> bool:
        return self.__Switch_normalOpen
    @Switch_normalOpen.setter
    def Switch_normalOpen(self, value: bool):
        if self.__Switch_normalOpen == None:
            self.__Switch_normalOpen = str(value).lower() == "true"
    @property
    def Switch_open(self) -> bool:
        return self.__Switch_open
    @Switch_open.setter
    def Switch_open(self, value: bool):
        if self.__Switch_open == None:
            self.__Switch_open = str(value).lower() == "true"
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}Switch' 
        if self.__Switch_Terminals != []:
            for item in self.__Switch_Terminals:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Switch.Terminals', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        if self.__Switch_mRID != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Switch.mRID')
            prop.text = str(self.__Switch_mRID)
        if self.__Switch_normalOpen != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Switch.normalOpen')
            prop.text = str(self.__Switch_normalOpen).lower()
        if self.__Switch_open != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Switch.open')
            prop.text = str(self.__Switch_open).lower()
        return root
    
    def validate(self):
        super().validate()
        minBound, maxBound = 1, float('Inf')
        if len(self.Switch_Terminals) < minBound or len(self.Switch_Terminals) > maxBound:
            raise ValueError('Incorrect multiplicity in Switch_Terminals')
        if any(not isinstance(item, Terminal) for item in self.Switch_Terminals):
            raise ValueError('Incorrect datatype in Switch_Terminals')
        if not isinstance(self.Switch_mRID, str):
            raise ValueError('Incorrect datatype in Switch_mRID')
        if not isinstance(self.Switch_normalOpen, bool) and self.Switch_normalOpen != None:
            raise ValueError('Incorrect datatype in Switch_normalOpen')
        if not isinstance(self.Switch_open, bool) and self.Switch_open != None:
            raise ValueError('Incorrect datatype in Switch_open')
 
class Terminal():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__Terminal_ConductingEquipment: 'EnergyConsumer' = None
        self.__Terminal_ConnectivityNode: 'ConnectivityNode' = None
        self.__Terminal_sequenceNumber: int = None
    @property
    def Terminal_ConductingEquipment(self) -> 'EnergyConsumer':
        return self.__Terminal_ConductingEquipment
    @Terminal_ConductingEquipment.setter
    def Terminal_ConductingEquipment(self, value: 'EnergyConsumer'):
        if self.__Terminal_ConductingEquipment == None:
            self.__Terminal_ConductingEquipment = value
            if isinstance(value.EnergyConsumer_Terminals, list):
                value.add_EnergyConsumer_Terminals(self)
            else:
                value.EnergyConsumer_Terminals = self
    @property
    def Terminal_ConnectivityNode(self) -> 'ConnectivityNode':
        return self.__Terminal_ConnectivityNode
    @Terminal_ConnectivityNode.setter
    def Terminal_ConnectivityNode(self, value: 'ConnectivityNode'):
        if self.__Terminal_ConnectivityNode == None:
            self.__Terminal_ConnectivityNode = value
            if isinstance(value.ConnectivityNode_Terminals, list):
                value.add_ConnectivityNode_Terminals(self)
            else:
                value.ConnectivityNode_Terminals = self
    @property
    def Terminal_sequenceNumber(self) -> int:
        return self.__Terminal_sequenceNumber
    @Terminal_sequenceNumber.setter
    def Terminal_sequenceNumber(self, value: int):
        if self.__Terminal_sequenceNumber == None:
            self.__Terminal_sequenceNumber = int(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Terminal', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__Terminal_ConductingEquipment != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Terminal.ConductingEquipment', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__Terminal_ConductingEquipment.URI})
        if self.__Terminal_ConnectivityNode != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Terminal.ConnectivityNode', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__Terminal_ConnectivityNode.URI})
        if self.__Terminal_sequenceNumber != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Terminal.sequenceNumber')
            prop.text = str(self.__Terminal_sequenceNumber)
        return root
    
    def validate(self):
        
        if not isinstance(self.Terminal_ConductingEquipment, EnergyConsumer):
            raise ValueError('Incorrect datatype in Terminal_ConductingEquipment')
        if not isinstance(self.Terminal_ConnectivityNode, ConnectivityNode) and self.Terminal_ConnectivityNode != None:
            raise ValueError('Incorrect datatype in Terminal_ConnectivityNode')
        if not isinstance(self.Terminal_sequenceNumber, int) and self.Terminal_sequenceNumber != None:
            raise ValueError('Incorrect datatype in Terminal_sequenceNumber')
 
class Voltage():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__Voltage_multiplier: 'UnitMultiplier' = None
        self.__Voltage_unit: 'UnitSymbol' = None
        self.__Voltage_value: Decimal = None
    @property
    def Voltage_multiplier(self) -> 'UnitMultiplier':
        return self.__Voltage_multiplier
    @Voltage_multiplier.setter
    def Voltage_multiplier(self, value: 'UnitMultiplier'):
        if self.__Voltage_multiplier == None:
            self.__Voltage_multiplier = value
    @property
    def Voltage_unit(self) -> 'UnitSymbol':
        return self.__Voltage_unit
    @Voltage_unit.setter
    def Voltage_unit(self, value: 'UnitSymbol'):
        if self.__Voltage_unit == None:
            self.__Voltage_unit = value
    @property
    def Voltage_value(self) -> Decimal:
        return self.__Voltage_value
    @Voltage_value.setter
    def Voltage_value(self, value: Decimal):
        if self.__Voltage_value == None:
            self.__Voltage_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Voltage', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__Voltage_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Voltage.multiplier')
            prop.text = str(self.__Voltage_multiplier)
        if self.__Voltage_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Voltage.unit')
            prop.text = str(self.__Voltage_unit)
        if self.__Voltage_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Voltage.value')
            prop.text = str(self.__Voltage_value)
        return root
    
    def validate(self):
        
        if not isinstance(self.Voltage_multiplier, UnitMultiplier) and self.Voltage_multiplier != None:
            raise ValueError('Incorrect datatype in Voltage_multiplier')
        if not isinstance(self.Voltage_unit, UnitSymbol) and self.Voltage_unit != None:
            raise ValueError('Incorrect datatype in Voltage_unit')
        if not isinstance(self.Voltage_value, Decimal):
            raise ValueError('Incorrect datatype in Voltage_value')
 
class ACLineSegment(Equipment):
    def __init__(self):
        super().__init__()
        self.__ACLineSegment_Terminals: List['Terminal'] = []
        self.__ACLineSegment_length: 'Length' = None
        self.__ACLineSegment_mRID: str = None
        self.__ACLineSegment_r: 'Resistance' = None
        self.__ACLineSegment_r0: 'Resistance' = None
        self.__ACLineSegment_x: 'Reactance' = None
        self.__ACLineSegment_x0: 'Reactance' = None
    def add_ACLineSegment_Terminals(self, value: 'Terminal'):
        if value not in self.__ACLineSegment_Terminals:
            self.__ACLineSegment_Terminals.append(value)
    @property
    def ACLineSegment_Terminals(self) -> List['Terminal']:
        return self.__ACLineSegment_Terminals
    @ACLineSegment_Terminals.setter
    def ACLineSegment_Terminals(self, list_objs: List['Terminal']):
        if self.__ACLineSegment_Terminals == []:
            self.__ACLineSegment_Terminals = list_objs
    @property
    def ACLineSegment_length(self) -> 'Length':
        return self.__ACLineSegment_length
    @ACLineSegment_length.setter
    def ACLineSegment_length(self, value: 'Length'):
        if self.__ACLineSegment_length == None:
            self.__ACLineSegment_length = value
    @property
    def ACLineSegment_mRID(self) -> str:
        return self.__ACLineSegment_mRID
    @ACLineSegment_mRID.setter
    def ACLineSegment_mRID(self, value: str):
        if self.__ACLineSegment_mRID == None:
            self.__ACLineSegment_mRID = str(value)
    @property
    def ACLineSegment_r(self) -> 'Resistance':
        return self.__ACLineSegment_r
    @ACLineSegment_r.setter
    def ACLineSegment_r(self, value: 'Resistance'):
        if self.__ACLineSegment_r == None:
            self.__ACLineSegment_r = value
    @property
    def ACLineSegment_r0(self) -> 'Resistance':
        return self.__ACLineSegment_r0
    @ACLineSegment_r0.setter
    def ACLineSegment_r0(self, value: 'Resistance'):
        if self.__ACLineSegment_r0 == None:
            self.__ACLineSegment_r0 = value
    @property
    def ACLineSegment_x(self) -> 'Reactance':
        return self.__ACLineSegment_x
    @ACLineSegment_x.setter
    def ACLineSegment_x(self, value: 'Reactance'):
        if self.__ACLineSegment_x == None:
            self.__ACLineSegment_x = value
    @property
    def ACLineSegment_x0(self) -> 'Reactance':
        return self.__ACLineSegment_x0
    @ACLineSegment_x0.setter
    def ACLineSegment_x0(self, value: 'Reactance'):
        if self.__ACLineSegment_x0 == None:
            self.__ACLineSegment_x0 = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}ACLineSegment' 
        if self.__ACLineSegment_Terminals != []:
            for item in self.__ACLineSegment_Terminals:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ACLineSegment.Terminals', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        if self.__ACLineSegment_length != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ACLineSegment.length', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__ACLineSegment_length.URI})
        if self.__ACLineSegment_mRID != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ACLineSegment.mRID')
            prop.text = str(self.__ACLineSegment_mRID)
        if self.__ACLineSegment_r != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ACLineSegment.r', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__ACLineSegment_r.URI})
        if self.__ACLineSegment_r0 != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ACLineSegment.r0', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__ACLineSegment_r0.URI})
        if self.__ACLineSegment_x != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ACLineSegment.x', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__ACLineSegment_x.URI})
        if self.__ACLineSegment_x0 != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ACLineSegment.x0', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__ACLineSegment_x0.URI})
        return root
    
    def validate(self):
        super().validate()
        minBound, maxBound = 1, float('Inf')
        if len(self.ACLineSegment_Terminals) < minBound or len(self.ACLineSegment_Terminals) > maxBound:
            raise ValueError('Incorrect multiplicity in ACLineSegment_Terminals')
        if any(not isinstance(item, Terminal) for item in self.ACLineSegment_Terminals):
            raise ValueError('Incorrect datatype in ACLineSegment_Terminals')
        if not isinstance(self.ACLineSegment_length, Length):
            raise ValueError('Incorrect datatype in ACLineSegment_length')
        if not isinstance(self.ACLineSegment_mRID, str):
            raise ValueError('Incorrect datatype in ACLineSegment_mRID')
        if not isinstance(self.ACLineSegment_r, Resistance):
            raise ValueError('Incorrect datatype in ACLineSegment_r')
        if not isinstance(self.ACLineSegment_r0, Resistance):
            raise ValueError('Incorrect datatype in ACLineSegment_r0')
        if not isinstance(self.ACLineSegment_x, Reactance):
            raise ValueError('Incorrect datatype in ACLineSegment_x')
        if not isinstance(self.ACLineSegment_x0, Reactance):
            raise ValueError('Incorrect datatype in ACLineSegment_x0')
 
class BusbarSection(Equipment):
    def __init__(self):
        super().__init__()
        self.__BusbarSection_Terminals: List['Terminal'] = []
        self.__BusbarSection_mRID: str = None
    def add_BusbarSection_Terminals(self, value: 'Terminal'):
        if value not in self.__BusbarSection_Terminals:
            self.__BusbarSection_Terminals.append(value)
    @property
    def BusbarSection_Terminals(self) -> List['Terminal']:
        return self.__BusbarSection_Terminals
    @BusbarSection_Terminals.setter
    def BusbarSection_Terminals(self, list_objs: List['Terminal']):
        if self.__BusbarSection_Terminals == []:
            self.__BusbarSection_Terminals = list_objs
    @property
    def BusbarSection_mRID(self) -> str:
        return self.__BusbarSection_mRID
    @BusbarSection_mRID.setter
    def BusbarSection_mRID(self, value: str):
        if self.__BusbarSection_mRID == None:
            self.__BusbarSection_mRID = str(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}BusbarSection' 
        if self.__BusbarSection_Terminals != []:
            for item in self.__BusbarSection_Terminals:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}BusbarSection.Terminals', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        if self.__BusbarSection_mRID != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}BusbarSection.mRID')
            prop.text = str(self.__BusbarSection_mRID)
        return root
    
    def validate(self):
        super().validate()
        minBound, maxBound = 0, float('Inf')
        if len(self.BusbarSection_Terminals) < minBound or len(self.BusbarSection_Terminals) > maxBound:
            raise ValueError('Incorrect multiplicity in BusbarSection_Terminals')
        if any(not isinstance(item, Terminal) for item in self.BusbarSection_Terminals):
            raise ValueError('Incorrect datatype in BusbarSection_Terminals')
        if not isinstance(self.BusbarSection_mRID, str):
            raise ValueError('Incorrect datatype in BusbarSection_mRID')
 
class EnergyConsumer(Equipment):
    def __init__(self):
        super().__init__()
        self.__EnergyConsumer_Terminals: 'Terminal' = None
        self.__EnergyConsumer_mRID: str = None
        self.__EnergyConsumer_p: 'ActivePower' = None
        self.__EnergyConsumer_q: 'ReactivePower' = None
    @property
    def EnergyConsumer_Terminals(self) -> 'Terminal':
        return self.__EnergyConsumer_Terminals
    @EnergyConsumer_Terminals.setter
    def EnergyConsumer_Terminals(self, value: 'Terminal'):
        if self.__EnergyConsumer_Terminals == None:
            self.__EnergyConsumer_Terminals = value
            if isinstance(value.Terminal_ConductingEquipment, list):
                value.add_Terminal_ConductingEquipment(self)
            else:
                value.Terminal_ConductingEquipment = self
    @property
    def EnergyConsumer_mRID(self) -> str:
        return self.__EnergyConsumer_mRID
    @EnergyConsumer_mRID.setter
    def EnergyConsumer_mRID(self, value: str):
        if self.__EnergyConsumer_mRID == None:
            self.__EnergyConsumer_mRID = str(value)
    @property
    def EnergyConsumer_p(self) -> 'ActivePower':
        return self.__EnergyConsumer_p
    @EnergyConsumer_p.setter
    def EnergyConsumer_p(self, value: 'ActivePower'):
        if self.__EnergyConsumer_p == None:
            self.__EnergyConsumer_p = value
    @property
    def EnergyConsumer_q(self) -> 'ReactivePower':
        return self.__EnergyConsumer_q
    @EnergyConsumer_q.setter
    def EnergyConsumer_q(self, value: 'ReactivePower'):
        if self.__EnergyConsumer_q == None:
            self.__EnergyConsumer_q = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}EnergyConsumer' 
        if self.__EnergyConsumer_Terminals != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EnergyConsumer.Terminals', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__EnergyConsumer_Terminals.URI})
        if self.__EnergyConsumer_mRID != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EnergyConsumer.mRID')
            prop.text = str(self.__EnergyConsumer_mRID)
        if self.__EnergyConsumer_p != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EnergyConsumer.p', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__EnergyConsumer_p.URI})
        if self.__EnergyConsumer_q != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EnergyConsumer.q', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__EnergyConsumer_q.URI})
        return root
    
    def validate(self):
        super().validate()
        if not isinstance(self.EnergyConsumer_Terminals, Terminal):
            raise ValueError('Incorrect datatype in EnergyConsumer_Terminals')
        if not isinstance(self.EnergyConsumer_mRID, str):
            raise ValueError('Incorrect datatype in EnergyConsumer_mRID')
        if not isinstance(self.EnergyConsumer_p, ActivePower):
            raise ValueError('Incorrect datatype in EnergyConsumer_p')
        if not isinstance(self.EnergyConsumer_q, ReactivePower):
            raise ValueError('Incorrect datatype in EnergyConsumer_q')
