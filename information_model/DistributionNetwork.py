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
        
        if not isinstance(self.ActivePower_multiplier, UnitMultiplier):
            raise ValueError('Incorrect datatype in ActivePower_multiplier')
        if not isinstance(self.ActivePower_unit, UnitSymbol):
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
        
        if not isinstance(self.ApparentPower_multiplier, UnitMultiplier):
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
        
        if not isinstance(self.Conductance_multiplier, UnitMultiplier):
            raise ValueError('Incorrect datatype in Conductance_multiplier')
        if not isinstance(self.Conductance_unit, UnitSymbol):
            raise ValueError('Incorrect datatype in Conductance_unit')
        if not isinstance(self.Conductance_value, Decimal):
            raise ValueError('Incorrect datatype in Conductance_value')
 
class IEC61970CIMVersion():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__IEC61970CIMVersion_date: 'date' = None
        self.__IEC61970CIMVersion_version: str = None
    @property
    def IEC61970CIMVersion_date(self) -> 'date':
        return self.__IEC61970CIMVersion_date
    @IEC61970CIMVersion_date.setter
    def IEC61970CIMVersion_date(self, value: 'date'):
        if self.__IEC61970CIMVersion_date == None:
            self.__IEC61970CIMVersion_date = value
    @property
    def IEC61970CIMVersion_version(self) -> str:
        return self.__IEC61970CIMVersion_version
    @IEC61970CIMVersion_version.setter
    def IEC61970CIMVersion_version(self, value: str):
        if self.__IEC61970CIMVersion_version == None:
            self.__IEC61970CIMVersion_version = str(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}IEC61970CIMVersion', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__IEC61970CIMVersion_date != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}IEC61970CIMVersion.date', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__IEC61970CIMVersion_date.URI})
        if self.__IEC61970CIMVersion_version != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}IEC61970CIMVersion.version')
            prop.text = str(self.__IEC61970CIMVersion_version)
        return root
    
    def validate(self):
        
        if not isinstance(self.IEC61970CIMVersion_date, date):
            raise ValueError('Incorrect datatype in IEC61970CIMVersion_date')
        if not isinstance(self.IEC61970CIMVersion_version, str):
            raise ValueError('Incorrect datatype in IEC61970CIMVersion_version')
 
class IdentifiedObject():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__IdentifiedObject_mRID: str = None
        self.__IdentifiedObject_name: str = None
    @property
    def IdentifiedObject_mRID(self) -> str:
        return self.__IdentifiedObject_mRID
    @IdentifiedObject_mRID.setter
    def IdentifiedObject_mRID(self, value: str):
        if self.__IdentifiedObject_mRID == None:
            self.__IdentifiedObject_mRID = str(value)
    @property
    def IdentifiedObject_name(self) -> str:
        return self.__IdentifiedObject_name
    @IdentifiedObject_name.setter
    def IdentifiedObject_name(self, value: str):
        if self.__IdentifiedObject_name == None:
            self.__IdentifiedObject_name = str(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}IdentifiedObject', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__IdentifiedObject_mRID != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}IdentifiedObject.mRID')
            prop.text = str(self.__IdentifiedObject_mRID)
        if self.__IdentifiedObject_name != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}IdentifiedObject.name')
            prop.text = str(self.__IdentifiedObject_name)
        return root
    
    def validate(self):
        
        if not isinstance(self.IdentifiedObject_mRID, str):
            raise ValueError('Incorrect datatype in IdentifiedObject_mRID')
        if not isinstance(self.IdentifiedObject_name, str) and self.IdentifiedObject_name != None:
            raise ValueError('Incorrect datatype in IdentifiedObject_name')
 
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
        
        if not isinstance(self.Length_multiplier, UnitMultiplier):
            raise ValueError('Incorrect datatype in Length_multiplier')
        if not isinstance(self.Length_unit, UnitSymbol):
            raise ValueError('Incorrect datatype in Length_unit')
        if not isinstance(self.Length_value, Decimal):
            raise ValueError('Incorrect datatype in Length_value')
 
class PowerSystemResource(IdentifiedObject):
    def __init__(self):
        super().__init__()
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}PowerSystemResource' 
        return root
    
    def validate(self):
        super().validate()
 
class PowerTransformerEnd():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__PowerTransformerEnd_PowerTransformer: 'PowerTransformer' = None
        self.__PowerTransformerEnd_connectionKind: 'WindingConnection' = None
        self.__PowerTransformerEnd_endNumber: int = None
        self.__PowerTransformerEnd_r: 'Resistance' = None
        self.__PowerTransformerEnd_r0: 'Resistance' = None
        self.__PowerTransformerEnd_ratedS: 'ApparentPower' = None
        self.__PowerTransformerEnd_ratedU: 'Voltage' = None
        self.__PowerTransformerEnd_x: 'Reactance' = None
        self.__PowerTransformerEnd_x0: 'Reactance' = None
    @property
    def PowerTransformerEnd_PowerTransformer(self) -> 'PowerTransformer':
        return self.__PowerTransformerEnd_PowerTransformer
    @PowerTransformerEnd_PowerTransformer.setter
    def PowerTransformerEnd_PowerTransformer(self, value: 'PowerTransformer'):
        if self.__PowerTransformerEnd_PowerTransformer == None:
            self.__PowerTransformerEnd_PowerTransformer = value
            if isinstance(value.PowerTransformer_PowerTransformerEnd, list):
                value.add_PowerTransformer_PowerTransformerEnd(self)
            else:
                value.PowerTransformer_PowerTransformerEnd = self
    @property
    def PowerTransformerEnd_connectionKind(self) -> 'WindingConnection':
        return self.__PowerTransformerEnd_connectionKind
    @PowerTransformerEnd_connectionKind.setter
    def PowerTransformerEnd_connectionKind(self, value: 'WindingConnection'):
        if self.__PowerTransformerEnd_connectionKind == None:
            self.__PowerTransformerEnd_connectionKind = value
    @property
    def PowerTransformerEnd_endNumber(self) -> int:
        return self.__PowerTransformerEnd_endNumber
    @PowerTransformerEnd_endNumber.setter
    def PowerTransformerEnd_endNumber(self, value: int):
        if self.__PowerTransformerEnd_endNumber == None:
            self.__PowerTransformerEnd_endNumber = int(value)
    @property
    def PowerTransformerEnd_r(self) -> 'Resistance':
        return self.__PowerTransformerEnd_r
    @PowerTransformerEnd_r.setter
    def PowerTransformerEnd_r(self, value: 'Resistance'):
        if self.__PowerTransformerEnd_r == None:
            self.__PowerTransformerEnd_r = value
    @property
    def PowerTransformerEnd_r0(self) -> 'Resistance':
        return self.__PowerTransformerEnd_r0
    @PowerTransformerEnd_r0.setter
    def PowerTransformerEnd_r0(self, value: 'Resistance'):
        if self.__PowerTransformerEnd_r0 == None:
            self.__PowerTransformerEnd_r0 = value
    @property
    def PowerTransformerEnd_ratedS(self) -> 'ApparentPower':
        return self.__PowerTransformerEnd_ratedS
    @PowerTransformerEnd_ratedS.setter
    def PowerTransformerEnd_ratedS(self, value: 'ApparentPower'):
        if self.__PowerTransformerEnd_ratedS == None:
            self.__PowerTransformerEnd_ratedS = value
    @property
    def PowerTransformerEnd_ratedU(self) -> 'Voltage':
        return self.__PowerTransformerEnd_ratedU
    @PowerTransformerEnd_ratedU.setter
    def PowerTransformerEnd_ratedU(self, value: 'Voltage'):
        if self.__PowerTransformerEnd_ratedU == None:
            self.__PowerTransformerEnd_ratedU = value
    @property
    def PowerTransformerEnd_x(self) -> 'Reactance':
        return self.__PowerTransformerEnd_x
    @PowerTransformerEnd_x.setter
    def PowerTransformerEnd_x(self, value: 'Reactance'):
        if self.__PowerTransformerEnd_x == None:
            self.__PowerTransformerEnd_x = value
    @property
    def PowerTransformerEnd_x0(self) -> 'Reactance':
        return self.__PowerTransformerEnd_x0
    @PowerTransformerEnd_x0.setter
    def PowerTransformerEnd_x0(self, value: 'Reactance'):
        if self.__PowerTransformerEnd_x0 == None:
            self.__PowerTransformerEnd_x0 = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__PowerTransformerEnd_PowerTransformer != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.PowerTransformer', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PowerTransformerEnd_PowerTransformer.URI})
        if self.__PowerTransformerEnd_connectionKind != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.connectionKind')
            prop.text = str(self.__PowerTransformerEnd_connectionKind)
        if self.__PowerTransformerEnd_endNumber != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.endNumber')
            prop.text = str(self.__PowerTransformerEnd_endNumber)
        if self.__PowerTransformerEnd_r != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.r', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PowerTransformerEnd_r.URI})
        if self.__PowerTransformerEnd_r0 != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.r0', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PowerTransformerEnd_r0.URI})
        if self.__PowerTransformerEnd_ratedS != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.ratedS', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PowerTransformerEnd_ratedS.URI})
        if self.__PowerTransformerEnd_ratedU != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.ratedU', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PowerTransformerEnd_ratedU.URI})
        if self.__PowerTransformerEnd_x != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.x', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PowerTransformerEnd_x.URI})
        if self.__PowerTransformerEnd_x0 != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.x0', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PowerTransformerEnd_x0.URI})
        return root
    
    def validate(self):
        
        if not isinstance(self.PowerTransformerEnd_PowerTransformer, PowerTransformer):
            raise ValueError('Incorrect datatype in PowerTransformerEnd_PowerTransformer')
        if not isinstance(self.PowerTransformerEnd_connectionKind, WindingConnection) and self.PowerTransformerEnd_connectionKind != None:
            raise ValueError('Incorrect datatype in PowerTransformerEnd_connectionKind')
        if not isinstance(self.PowerTransformerEnd_endNumber, int):
            raise ValueError('Incorrect datatype in PowerTransformerEnd_endNumber')
        if not isinstance(self.PowerTransformerEnd_r, Resistance) and self.PowerTransformerEnd_r != None:
            raise ValueError('Incorrect datatype in PowerTransformerEnd_r')
        if not isinstance(self.PowerTransformerEnd_r0, Resistance) and self.PowerTransformerEnd_r0 != None:
            raise ValueError('Incorrect datatype in PowerTransformerEnd_r0')
        if not isinstance(self.PowerTransformerEnd_ratedS, ApparentPower):
            raise ValueError('Incorrect datatype in PowerTransformerEnd_ratedS')
        if not isinstance(self.PowerTransformerEnd_ratedU, Voltage):
            raise ValueError('Incorrect datatype in PowerTransformerEnd_ratedU')
        if not isinstance(self.PowerTransformerEnd_x, Reactance) and self.PowerTransformerEnd_x != None:
            raise ValueError('Incorrect datatype in PowerTransformerEnd_x')
        if not isinstance(self.PowerTransformerEnd_x0, Reactance) and self.PowerTransformerEnd_x0 != None:
            raise ValueError('Incorrect datatype in PowerTransformerEnd_x0')
 
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
        
        if not isinstance(self.Reactance_multiplier, UnitMultiplier):
            raise ValueError('Incorrect datatype in Reactance_multiplier')
        if not isinstance(self.Reactance_unit, UnitSymbol):
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
        
        if not isinstance(self.ReactivePower_multiplier, UnitMultiplier):
            raise ValueError('Incorrect datatype in ReactivePower_multiplier')
        if not isinstance(self.ReactivePower_unit, UnitSymbol):
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
        
        if not isinstance(self.Resistance_multiplier, UnitMultiplier):
            raise ValueError('Incorrect datatype in Resistance_multiplier')
        if not isinstance(self.Resistance_unit, UnitSymbol):
            raise ValueError('Incorrect datatype in Resistance_unit')
        if not isinstance(self.Resistance_value, Decimal):
            raise ValueError('Incorrect datatype in Resistance_value')
 
class Substation():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__Substation_SubstationFeeder: List['Feeder'] = []
    def add_Substation_SubstationFeeder(self, value: 'Feeder'):
        if value not in self.__Substation_SubstationFeeder:
            self.__Substation_SubstationFeeder.append(value)
    @property
    def Substation_SubstationFeeder(self) -> List['Feeder']:
        return self.__Substation_SubstationFeeder
    @Substation_SubstationFeeder.setter
    def Substation_SubstationFeeder(self, list_objs: List['Feeder']):
        if self.__Substation_SubstationFeeder == []:
            self.__Substation_SubstationFeeder = list_objs
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Substation', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__Substation_SubstationFeeder != []:
            for item in self.__Substation_SubstationFeeder:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Substation.SubstationFeeder', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        return root
    
    def validate(self):
        
        minBound, maxBound = 0, float('Inf')
        if len(self.Substation_SubstationFeeder) < minBound or len(self.Substation_SubstationFeeder) > maxBound:
            raise ValueError('Incorrect multiplicity in Substation_SubstationFeeder')
        if any(not isinstance(item, Feeder) for item in self.Substation_SubstationFeeder):
            raise ValueError('Incorrect datatype in Substation_SubstationFeeder')
 
class Susceptance():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__Susceptance_multiplier: 'UnitMultiplier' = None
        self.__Susceptance_unit: 'UnitSymbol' = None
        self.__Susceptance_value: Decimal = None
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
    @property
    def Susceptance_value(self) -> Decimal:
        return self.__Susceptance_value
    @Susceptance_value.setter
    def Susceptance_value(self, value: Decimal):
        if self.__Susceptance_value == None:
            self.__Susceptance_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Susceptance', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.__Susceptance_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Susceptance.multiplier')
            prop.text = str(self.__Susceptance_multiplier)
        if self.__Susceptance_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Susceptance.unit')
            prop.text = str(self.__Susceptance_unit)
        if self.__Susceptance_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Susceptance.value')
            prop.text = str(self.__Susceptance_value)
        return root
    
    def validate(self):
        
        if not isinstance(self.Susceptance_multiplier, UnitMultiplier):
            raise ValueError('Incorrect datatype in Susceptance_multiplier')
        if not isinstance(self.Susceptance_unit, UnitSymbol):
            raise ValueError('Incorrect datatype in Susceptance_unit')
        if not isinstance(self.Susceptance_value, Decimal):
            raise ValueError('Incorrect datatype in Susceptance_value')
 
class Terminal():
    def __init__(self):
        self.URI = '#' + str(uuid())
        self.__Terminal_ConductingEquipment: 'ConductingEquipment' = None
        self.__Terminal_ConnectivityNode: 'ConnectivityNode' = None
        self.__Terminal_sequenceNumber: int = None
    @property
    def Terminal_ConductingEquipment(self) -> 'ConductingEquipment':
        return self.__Terminal_ConductingEquipment
    @Terminal_ConductingEquipment.setter
    def Terminal_ConductingEquipment(self, value: 'ConductingEquipment'):
        if self.__Terminal_ConductingEquipment == None:
            self.__Terminal_ConductingEquipment = value
            if isinstance(value.ConductingEquipment_Terminals, list):
                value.add_ConductingEquipment_Terminals(self)
            else:
                value.ConductingEquipment_Terminals = self
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
        
        if not isinstance(self.Terminal_ConductingEquipment, ConductingEquipment):
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
        
        if not isinstance(self.Voltage_multiplier, UnitMultiplier):
            raise ValueError('Incorrect datatype in Voltage_multiplier')
        if not isinstance(self.Voltage_unit, UnitSymbol) and self.Voltage_unit != None:
            raise ValueError('Incorrect datatype in Voltage_unit')
        if not isinstance(self.Voltage_value, Decimal):
            raise ValueError('Incorrect datatype in Voltage_value')
 
class ConnectivityNode(IdentifiedObject):
    def __init__(self):
        super().__init__()
        self.__ConnectivityNode_Terminals: List['Terminal'] = []
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
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}ConnectivityNode' 
        if self.__ConnectivityNode_Terminals != []:
            for item in self.__ConnectivityNode_Terminals:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ConnectivityNode.Terminals', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        return root
    
    def validate(self):
        super().validate()
        minBound, maxBound = 0, float('Inf')
        if len(self.ConnectivityNode_Terminals) < minBound or len(self.ConnectivityNode_Terminals) > maxBound:
            raise ValueError('Incorrect multiplicity in ConnectivityNode_Terminals')
        if any(not isinstance(item, Terminal) for item in self.ConnectivityNode_Terminals):
            raise ValueError('Incorrect datatype in ConnectivityNode_Terminals')
 
class Equipment(PowerSystemResource):
    def __init__(self):
        super().__init__()
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}Equipment' 
        return root
    
    def validate(self):
        super().validate()
 
class EquipmentContainer(PowerSystemResource):
    def __init__(self):
        super().__init__()
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}EquipmentContainer' 
        return root
    
    def validate(self):
        super().validate()
 
class Feeder(EquipmentContainer):
    def __init__(self):
        super().__init__()
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}Feeder' 
        return root
    
    def validate(self):
        super().validate()
 
class Line(EquipmentContainer):
    def __init__(self):
        super().__init__()
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}Line' 
        return root
    
    def validate(self):
        super().validate()
 
class ConductingEquipment(Equipment):
    def __init__(self):
        super().__init__()
        self.__ConductingEquipment_Terminals: List['Terminal'] = []
    def add_ConductingEquipment_Terminals(self, value: 'Terminal'):
        if value not in self.__ConductingEquipment_Terminals:
            self.__ConductingEquipment_Terminals.append(value)
            if isinstance(value.Terminal_ConductingEquipment, list):
                value.add_Terminal_ConductingEquipment(self)
            else:
                value.Terminal_ConductingEquipment = self
    @property
    def ConductingEquipment_Terminals(self) -> List['Terminal']:
        return self.__ConductingEquipment_Terminals
    @ConductingEquipment_Terminals.setter
    def ConductingEquipment_Terminals(self, list_objs: List['Terminal']):
        if self.__ConductingEquipment_Terminals == []:
            self.__ConductingEquipment_Terminals = list_objs
            if isinstance(list_objs[0].Terminal_ConductingEquipment, list):
                for obj in list_objs:
                    obj.add_Terminal_ConductingEquipment(self)
            else:
                for obj in list_objs:
                    obj.Terminal_ConductingEquipment = self
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}ConductingEquipment' 
        if self.__ConductingEquipment_Terminals != []:
            for item in self.__ConductingEquipment_Terminals:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ConductingEquipment.Terminals', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        return root
    
    def validate(self):
        super().validate()
        minBound, maxBound = 0, float('Inf')
        if len(self.ConductingEquipment_Terminals) < minBound or len(self.ConductingEquipment_Terminals) > maxBound:
            raise ValueError('Incorrect multiplicity in ConductingEquipment_Terminals')
        if any(not isinstance(item, Terminal) for item in self.ConductingEquipment_Terminals):
            raise ValueError('Incorrect datatype in ConductingEquipment_Terminals')
 
class Conductor(ConductingEquipment):
    def __init__(self):
        super().__init__()
        self.__Conductor_length: 'Length' = None
    @property
    def Conductor_length(self) -> 'Length':
        return self.__Conductor_length
    @Conductor_length.setter
    def Conductor_length(self, value: 'Length'):
        if self.__Conductor_length == None:
            self.__Conductor_length = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}Conductor' 
        if self.__Conductor_length != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Conductor.length', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__Conductor_length.URI})
        return root
    
    def validate(self):
        super().validate()
        if not isinstance(self.Conductor_length, Length):
            raise ValueError('Incorrect datatype in Conductor_length')
 
class EnergyConsumer(ConductingEquipment):
    def __init__(self):
        super().__init__()
        self.__EnergyConsumer_p: 'ActivePower' = None
        self.__EnergyConsumer_q: 'ReactivePower' = None
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
        if self.__EnergyConsumer_p != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EnergyConsumer.p', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__EnergyConsumer_p.URI})
        if self.__EnergyConsumer_q != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EnergyConsumer.q', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__EnergyConsumer_q.URI})
        return root
    
    def validate(self):
        super().validate()
        if not isinstance(self.EnergyConsumer_p, ActivePower):
            raise ValueError('Incorrect datatype in EnergyConsumer_p')
        if not isinstance(self.EnergyConsumer_q, ReactivePower):
            raise ValueError('Incorrect datatype in EnergyConsumer_q')
 
class EquivalentInjection(ConductingEquipment):
    def __init__(self):
        super().__init__()
        self.__EquivalentInjection_BaseVoltage: 'BaseVoltage' = None
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
        if not isinstance(self.EquivalentInjection_r, Resistance) and self.EquivalentInjection_r != None:
            raise ValueError('Incorrect datatype in EquivalentInjection_r')
        if not isinstance(self.EquivalentInjection_r0, Resistance) and self.EquivalentInjection_r0 != None:
            raise ValueError('Incorrect datatype in EquivalentInjection_r0')
        if not isinstance(self.EquivalentInjection_x, Reactance) and self.EquivalentInjection_x != None:
            raise ValueError('Incorrect datatype in EquivalentInjection_x')
        if not isinstance(self.EquivalentInjection_x0, Reactance) and self.EquivalentInjection_x0 != None:
            raise ValueError('Incorrect datatype in EquivalentInjection_x0')
 
class PowerTransformer(ConductingEquipment):
    def __init__(self):
        super().__init__()
        self.__PowerTransformer_PowerTransformerEnd: List['PowerTransformerEnd'] = []
    def add_PowerTransformer_PowerTransformerEnd(self, value: 'PowerTransformerEnd'):
        if value not in self.__PowerTransformer_PowerTransformerEnd:
            self.__PowerTransformer_PowerTransformerEnd.append(value)
            if isinstance(value.PowerTransformerEnd_PowerTransformer, list):
                value.add_PowerTransformerEnd_PowerTransformer(self)
            else:
                value.PowerTransformerEnd_PowerTransformer = self
    @property
    def PowerTransformer_PowerTransformerEnd(self) -> List['PowerTransformerEnd']:
        return self.__PowerTransformer_PowerTransformerEnd
    @PowerTransformer_PowerTransformerEnd.setter
    def PowerTransformer_PowerTransformerEnd(self, list_objs: List['PowerTransformerEnd']):
        if self.__PowerTransformer_PowerTransformerEnd == []:
            self.__PowerTransformer_PowerTransformerEnd = list_objs
            if isinstance(list_objs[0].PowerTransformerEnd_PowerTransformer, list):
                for obj in list_objs:
                    obj.add_PowerTransformerEnd_PowerTransformer(self)
            else:
                for obj in list_objs:
                    obj.PowerTransformerEnd_PowerTransformer = self
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}PowerTransformer' 
        if self.__PowerTransformer_PowerTransformerEnd != []:
            for item in self.__PowerTransformer_PowerTransformerEnd:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformer.PowerTransformerEnd', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        return root
    
    def validate(self):
        super().validate()
        minBound, maxBound = 1, float('Inf')
        if len(self.PowerTransformer_PowerTransformerEnd) < minBound or len(self.PowerTransformer_PowerTransformerEnd) > maxBound:
            raise ValueError('Incorrect multiplicity in PowerTransformer_PowerTransformerEnd')
        if any(not isinstance(item, PowerTransformerEnd) for item in self.PowerTransformer_PowerTransformerEnd):
            raise ValueError('Incorrect datatype in PowerTransformer_PowerTransformerEnd')
 
class Switch(ConductingEquipment):
    def __init__(self):
        super().__init__()
        self.__Switch_normalOpen: bool = None
        self.__Switch_open: bool = None
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
        if self.__Switch_normalOpen != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Switch.normalOpen')
            prop.text = str(self.__Switch_normalOpen).lower()
        if self.__Switch_open != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Switch.open')
            prop.text = str(self.__Switch_open).lower()
        return root
    
    def validate(self):
        super().validate()
        if not isinstance(self.Switch_normalOpen, bool) and self.Switch_normalOpen != None:
            raise ValueError('Incorrect datatype in Switch_normalOpen')
        if not isinstance(self.Switch_open, bool) and self.Switch_open != None:
            raise ValueError('Incorrect datatype in Switch_open')
 
class ACLineSegment(Conductor):
    def __init__(self):
        super().__init__()
        self.__ACLineSegment_r: 'Resistance' = None
        self.__ACLineSegment_r0: 'Resistance' = None
        self.__ACLineSegment_x: 'Reactance' = None
        self.__ACLineSegment_x0: 'Reactance' = None
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
        if not isinstance(self.ACLineSegment_r, Resistance):
            raise ValueError('Incorrect datatype in ACLineSegment_r')
        if not isinstance(self.ACLineSegment_r0, Resistance):
            raise ValueError('Incorrect datatype in ACLineSegment_r0')
        if not isinstance(self.ACLineSegment_x, Reactance):
            raise ValueError('Incorrect datatype in ACLineSegment_x')
        if not isinstance(self.ACLineSegment_x0, Reactance):
            raise ValueError('Incorrect datatype in ACLineSegment_x0')
 
class BusbarSection(ConductingEquipment):
    def __init__(self):
        super().__init__()
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}BusbarSection' 
        return root
    
    def validate(self):
        super().validate()
