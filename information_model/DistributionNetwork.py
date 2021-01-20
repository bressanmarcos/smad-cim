from decimal import Decimal
from enum import Enum
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
__ID_ATTRIB = '{'+__RDF_NS+'}ID'
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

def _import(root):
    def get_type(element):
        if element.tag == __DESCRIPTION_TAG:
            return element.find(__TYPE_TAG).attrib[__RESOURCE_ATTRIB].split('#')[1]
        return element.tag.split('}')[1]
    def get_element_URI(element):
        try:
            return __BASE_NS.replace('#','') + '#' + element.attrib[__ID_ATTRIB]
        except:
            return __BASE_NS.replace('#','') + element.attrib[__ABOUT_ATTRIB]

    instances_dict = {}

    try:
        __BASE_NS = root.attrib[__XML_BASE].replace('#', '') + '#'
    except:
        __BASE_NS = ''

    # Instance resouces and set URI
    for child in root:
        resource_type = get_type(child)
        uri = '#' + get_element_URI(child).split('#')[1]
        instances_dict[uri] = eval(f'{resource_type}()')
        instances_dict[uri].URI = uri

    # Set resources attributes
    for child in root:
        uri = '#' + get_element_URI(child).split('#')[1]
        instance = instances_dict[uri]
        for resource_item in child:
            dtype = get_type(resource_item).split('.')[1]
            instance_attribute = getattr(instance, dtype)
            if __RESOURCE_ATTRIB in resource_item.attrib:
                referenced_resource_uri = resource_item.attrib[__RESOURCE_ATTRIB]
                value = instances_dict[referenced_resource_uri]
            else:
                value = resource_item.text
            if isinstance(instance_attribute, list):
                add_method = getattr(instance, f'add_{dtype}')
                add_method(value)
            else:
                setattr(instance, dtype, value)

    return instances_dict

class DocumentCIMRDF():
    PRIMITIVES = (Decimal, str, int, bool)

    def __init__(self, resources = []):
        self.resources = []
        for resource in resources:
            self.resources.append(resource)

    def add_elements(self, elements: Union[ET.Element, List[ET.Element]]):
        elements = elements if isinstance(elements, list) else [elements]
        for element in elements:
            if element not in self.resources:
                self.resources.append(element)

    def add_recursively(self, elements: Union[ET.Element, List[ET.Element]]):
        elements = elements if isinstance(elements, list) else [elements]
        for element in elements:
            if element not in self.resources and element != None and all(not isinstance(element, primitive) for primitive in DocumentCIMRDF.PRIMITIVES) and not isinstance(element, Enum):
                self.resources.append(element)
                for intern_element in element.__dict__.values():
                    self.add_recursively(intern_element)

    def dump(self):
        rough_string = self.tostring()
        reparsed = parseString(rough_string)
        print(reparsed.toprettyxml(indent=' '*4))
    
    def pack(self):
        root = ET.Element('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF', attrib={'{http://www.w3.org/XML/1998/namespace}base': 'grei.ufc.br/DistributionNetwork/new_resource#'})
        for element in self.resources:
            root.append(element.serialize())
        return ET.ElementTree(root)

    def tostring(self):
        root = self.pack().getroot()
        return ET.tostring(root)

    def fromstring(self, xml):
        root = ET.fromstring(xml)
        self.resources = list(_import(root).values())

    def tofile(self, filename):
        etree = self.pack()
        etree.write(filename)

    def fromfile(self, filename):
        root = ET.parse(filename).getroot()
        self.resources = list(_import(root).values())


class PhaseShuntConnectionKind(str, Enum):
    """The configuration of phase connections for a single terminal device such as a load or capacitor."""
    D = 'D' # Delta connection. 
    Y = 'Y' # Wye connection. 
    Yn = 'Yn' # Wye, with neutral brought out for grounding. 

class UnitMultiplier(str, Enum):
    """The unit multipliers defined for the CIM.  When applied to unit symbols that already contain a multiplier, both multipliers are used. For example, to exchange kilograms using unit symbol of kg, one uses the "none" multiplier, to exchange metric ton (Mg), one uses the "k" multiplier."""
    G = 'G' # Giga 10**9. 
    M = 'M' # Mega 10**6. 
    k = 'k' # Kilo 10**3. 
    m = 'm' # Milli 10**-3. 
    micro = 'micro' # Micro 10**-6. 
    none = 'none' # No multiplier or equivalently multiply by 1. 

class UnitSymbol(str, Enum):
    """The units defined for usage in the CIM."""
    A = 'A' # Current in Ampere. 
    SPerm = 'SPerm' # Conductance per length (F/m). 
    V = 'V' # Electric potential in Volt (W/A). 
    VA = 'VA' # Apparent power in Volt Ampere (See also real power and reactive power.) 
    VAr = 'VAr' # Reactive power in Volt Ampere reactive. The “reactive” or “imaginary” component of electrical power (VIsin(phi)). (See also real power and apparent power). Note: Different meter designs use different methods to arrive at their results. Some meters may compute reactive power as an arithmetic value, while others compute the value vectorially. The data consumer should determine the method in use and the suitability of the measurement for the intended purpose. 
    W = 'W' # Real power in Watt (J/s). Electrical power may have real and reactive components. The real portion of electrical power (I²R or VIcos(phi)), is expressed in Watts. (See also apparent power and reactive power.) 
    m = 'm' # Length in meter. 
    ohm = 'ohm' # Electric resistance in ohm (V/A). 
    ohmPerm = 'ohmPerm' # Electric resistance per length in ohm per metre ((V/A)/m). 

class WindingConnection(str, Enum):
    """Winding connection type."""
    D = 'D' # Delta 
    Y = 'Y' # Wye 
    Yn = 'Yn' # Wye, with neutral brought out for grounding. 
    Z = 'Z' # ZigZag 
    Zn = 'Zn' # ZigZag, with neutral brought out for grounding. 
 
class ActivePower():
    """Product of RMS value of the voltage and the RMS value of the in-phase component of the current."""
    def __init__(self, multiplier: 'UnitMultiplier' = None, unit: 'UnitSymbol' = None, value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.multiplier = multiplier
        self.unit = unit
        self.value = value
    @property
    def multiplier(self) -> 'UnitMultiplier':
        return self.__multiplier
    @multiplier.setter
    def multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__multiplier = None
        elif not hasattr(self, 'multiplier') or self.multiplier is not value:
            self.__multiplier = UnitMultiplier(value)
    @property
    def unit(self) -> 'UnitSymbol':
        return self.__unit
    @unit.setter
    def unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__unit = None
        elif not hasattr(self, 'unit') or self.unit is not value:
            self.__unit = UnitSymbol(value)
    @property
    def value(self) -> Decimal:
        return self.__value
    @value.setter
    def value(self, value: Decimal):
        if value == None:
            self.__value = None
        elif not hasattr(self, 'value') or self.value is not value:
            self.__value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}ActivePower', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ActivePower.multiplier')
            prop.text = self.multiplier.value
        if self.unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ActivePower.unit')
            prop.text = self.unit.value
        if self.value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ActivePower.value')
            prop.text = str(self.value)
        return root
    def validate(self):
        if not isinstance(self.multiplier, UnitMultiplier):
            raise ValueError(f'Incorrect datatype in multiplier [ActivePower] (expected UnitMultiplier but encountered {self.multiplier.__class__.__name__} instead)')
        if not isinstance(self.unit, UnitSymbol):
            raise ValueError(f'Incorrect datatype in unit [ActivePower] (expected UnitSymbol but encountered {self.unit.__class__.__name__} instead)')
        if not isinstance(self.value, Decimal):
            raise ValueError(f'Incorrect datatype in value [ActivePower] (expected Decimal but encountered {self.value.__class__.__name__} instead)')
 
class ApparentPower():
    """Product of the RMS value of the voltage and the RMS value of the current."""
    def __init__(self, multiplier: 'UnitMultiplier' = None, unit: 'UnitSymbol' = None, value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.multiplier = multiplier
        self.unit = unit
        self.value = value
    @property
    def multiplier(self) -> 'UnitMultiplier':
        return self.__multiplier
    @multiplier.setter
    def multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__multiplier = None
        elif not hasattr(self, 'multiplier') or self.multiplier is not value:
            self.__multiplier = UnitMultiplier(value)
    @property
    def unit(self) -> 'UnitSymbol':
        return self.__unit
    @unit.setter
    def unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__unit = None
        elif not hasattr(self, 'unit') or self.unit is not value:
            self.__unit = UnitSymbol(value)
    @property
    def value(self) -> Decimal:
        return self.__value
    @value.setter
    def value(self, value: Decimal):
        if value == None:
            self.__value = None
        elif not hasattr(self, 'value') or self.value is not value:
            self.__value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}ApparentPower', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ApparentPower.multiplier')
            prop.text = self.multiplier.value
        if self.unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ApparentPower.unit')
            prop.text = self.unit.value
        if self.value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ApparentPower.value')
            prop.text = str(self.value)
        return root
    def validate(self):
        if not isinstance(self.multiplier, UnitMultiplier) and self.multiplier != None:
            raise ValueError(f'Incorrect datatype in multiplier [ApparentPower] (expected UnitMultiplier but encountered {self.multiplier.__class__.__name__} instead)')
        if not isinstance(self.unit, UnitSymbol) and self.unit != None:
            raise ValueError(f'Incorrect datatype in unit [ApparentPower] (expected UnitSymbol but encountered {self.unit.__class__.__name__} instead)')
        if not isinstance(self.value, Decimal) and self.value != None:
            raise ValueError(f'Incorrect datatype in value [ApparentPower] (expected Decimal but encountered {self.value.__class__.__name__} instead)')
 
class BaseVoltage():
    """Defines a system base voltage which is referenced."""
    def __init__(self, nominalVoltage: 'Voltage' = None):
        self.URI = '#' + str(uuid())
        # The power system resource's base voltage. 
        self.nominalVoltage = nominalVoltage
    @property
    def nominalVoltage(self) -> 'Voltage':
        return self.__nominalVoltage
    @nominalVoltage.setter
    def nominalVoltage(self, value: 'Voltage'):
        if value == None:
            self.__nominalVoltage = None
        elif not hasattr(self, 'nominalVoltage') or self.nominalVoltage is not value:
            self.__nominalVoltage = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}BaseVoltage', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.nominalVoltage != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}BaseVoltage.nominalVoltage', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__nominalVoltage.URI})
        return root
    def validate(self):
        if not isinstance(self.nominalVoltage, Voltage):
            raise ValueError(f'Incorrect datatype in nominalVoltage [BaseVoltage] (expected Voltage but encountered {self.nominalVoltage.__class__.__name__} instead)')
 
class Conductance():
    """Factor by which voltage must be multiplied to give corresponding power lost from a circuit. Real part of admittance."""
    def __init__(self, multiplier: 'UnitMultiplier' = None, unit: 'UnitSymbol' = None, value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.multiplier = multiplier
        self.unit = unit
        self.value = value
    @property
    def multiplier(self) -> 'UnitMultiplier':
        return self.__multiplier
    @multiplier.setter
    def multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__multiplier = None
        elif not hasattr(self, 'multiplier') or self.multiplier is not value:
            self.__multiplier = UnitMultiplier(value)
    @property
    def unit(self) -> 'UnitSymbol':
        return self.__unit
    @unit.setter
    def unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__unit = None
        elif not hasattr(self, 'unit') or self.unit is not value:
            self.__unit = UnitSymbol(value)
    @property
    def value(self) -> Decimal:
        return self.__value
    @value.setter
    def value(self, value: Decimal):
        if value == None:
            self.__value = None
        elif not hasattr(self, 'value') or self.value is not value:
            self.__value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Conductance', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Conductance.multiplier')
            prop.text = self.multiplier.value
        if self.unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Conductance.unit')
            prop.text = self.unit.value
        if self.value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Conductance.value')
            prop.text = str(self.value)
        return root
    def validate(self):
        if not isinstance(self.multiplier, UnitMultiplier):
            raise ValueError(f'Incorrect datatype in multiplier [Conductance] (expected UnitMultiplier but encountered {self.multiplier.__class__.__name__} instead)')
        if not isinstance(self.unit, UnitSymbol):
            raise ValueError(f'Incorrect datatype in unit [Conductance] (expected UnitSymbol but encountered {self.unit.__class__.__name__} instead)')
        if not isinstance(self.value, Decimal):
            raise ValueError(f'Incorrect datatype in value [Conductance] (expected Decimal but encountered {self.value.__class__.__name__} instead)')
 
class ConductancePerLength():
    """Real part of admittance per unit of length."""
    def __init__(self, multiplier: 'UnitMultiplier' = None, unit: 'UnitSymbol' = None, value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.multiplier = multiplier
        self.unit = unit
        self.value = value
    @property
    def multiplier(self) -> 'UnitMultiplier':
        return self.__multiplier
    @multiplier.setter
    def multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__multiplier = None
        elif not hasattr(self, 'multiplier') or self.multiplier is not value:
            self.__multiplier = UnitMultiplier(value)
    @property
    def unit(self) -> 'UnitSymbol':
        return self.__unit
    @unit.setter
    def unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__unit = None
        elif not hasattr(self, 'unit') or self.unit is not value:
            self.__unit = UnitSymbol(value)
    @property
    def value(self) -> Decimal:
        return self.__value
    @value.setter
    def value(self, value: Decimal):
        if value == None:
            self.__value = None
        elif not hasattr(self, 'value') or self.value is not value:
            self.__value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}ConductancePerLength', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ConductancePerLength.multiplier')
            prop.text = self.multiplier.value
        if self.unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ConductancePerLength.unit')
            prop.text = self.unit.value
        if self.value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ConductancePerLength.value')
            prop.text = str(self.value)
        return root
    def validate(self):
        if not isinstance(self.multiplier, UnitMultiplier) and self.multiplier != None:
            raise ValueError(f'Incorrect datatype in multiplier [ConductancePerLength] (expected UnitMultiplier but encountered {self.multiplier.__class__.__name__} instead)')
        if not isinstance(self.unit, UnitSymbol) and self.unit != None:
            raise ValueError(f'Incorrect datatype in unit [ConductancePerLength] (expected UnitSymbol but encountered {self.unit.__class__.__name__} instead)')
        if not isinstance(self.value, Decimal) and self.value != None:
            raise ValueError(f'Incorrect datatype in value [ConductancePerLength] (expected Decimal but encountered {self.value.__class__.__name__} instead)')
 
class CurrentFlow():
    """Electrical current with sign convention: positive flow is out of the conducting equipment into the connectivity node. Can be both AC and DC."""
    def __init__(self, multiplier: 'UnitMultiplier' = None, unit: 'UnitSymbol' = None, value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.multiplier = multiplier
        self.unit = unit
        self.value = value
    @property
    def multiplier(self) -> 'UnitMultiplier':
        return self.__multiplier
    @multiplier.setter
    def multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__multiplier = None
        elif not hasattr(self, 'multiplier') or self.multiplier is not value:
            self.__multiplier = UnitMultiplier(value)
    @property
    def unit(self) -> 'UnitSymbol':
        return self.__unit
    @unit.setter
    def unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__unit = None
        elif not hasattr(self, 'unit') or self.unit is not value:
            self.__unit = UnitSymbol(value)
    @property
    def value(self) -> Decimal:
        return self.__value
    @value.setter
    def value(self, value: Decimal):
        if value == None:
            self.__value = None
        elif not hasattr(self, 'value') or self.value is not value:
            self.__value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}CurrentFlow', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}CurrentFlow.multiplier')
            prop.text = self.multiplier.value
        if self.unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}CurrentFlow.unit')
            prop.text = self.unit.value
        if self.value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}CurrentFlow.value')
            prop.text = str(self.value)
        return root
    def validate(self):
        if not isinstance(self.multiplier, UnitMultiplier) and self.multiplier != None:
            raise ValueError(f'Incorrect datatype in multiplier [CurrentFlow] (expected UnitMultiplier but encountered {self.multiplier.__class__.__name__} instead)')
        if not isinstance(self.unit, UnitSymbol) and self.unit != None:
            raise ValueError(f'Incorrect datatype in unit [CurrentFlow] (expected UnitSymbol but encountered {self.unit.__class__.__name__} instead)')
        if not isinstance(self.value, Decimal) and self.value != None:
            raise ValueError(f'Incorrect datatype in value [CurrentFlow] (expected Decimal but encountered {self.value.__class__.__name__} instead)')
 
class IdentifiedObject():
    """This is a root class to provide common identification for all classes needing identification and naming attributes."""
    def __init__(self, mRID: str = None, name: str = None):
        self.URI = '#' + str(uuid())
        # Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID,  as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended. For CIMXML data files in RDF syntax conforming to IEC 61970-552 Edition 1, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements. 
        self.mRID = mRID
        # The name is any free human readable and possibly non unique text naming the object. 
        self.name = name
    @property
    def mRID(self) -> str:
        return self.__mRID
    @mRID.setter
    def mRID(self, value: str):
        if value == None:
            self.__mRID = None
        elif not hasattr(self, 'mRID') or self.mRID is not value:
            self.__mRID = str(value)
    @property
    def name(self) -> str:
        return self.__name
    @name.setter
    def name(self, value: str):
        if value == None:
            self.__name = None
        elif not hasattr(self, 'name') or self.name is not value:
            self.__name = str(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}IdentifiedObject', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.mRID != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}IdentifiedObject.mRID')
            prop.text = str(self.mRID)
        if self.name != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}IdentifiedObject.name')
            prop.text = str(self.name)
        return root
    def validate(self):
        if not isinstance(self.mRID, str):
            raise ValueError(f'Incorrect datatype in mRID [IdentifiedObject] (expected str but encountered {self.mRID.__class__.__name__} instead)')
        if not isinstance(self.name, str) and self.name != None:
            raise ValueError(f'Incorrect datatype in name [IdentifiedObject] (expected str but encountered {self.name.__class__.__name__} instead)')
 
class Length():
    """Unit of length. Never negative."""
    def __init__(self, multiplier: 'UnitMultiplier' = None, unit: 'UnitSymbol' = None, value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.multiplier = multiplier
        self.unit = unit
        self.value = value
    @property
    def multiplier(self) -> 'UnitMultiplier':
        return self.__multiplier
    @multiplier.setter
    def multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__multiplier = None
        elif not hasattr(self, 'multiplier') or self.multiplier is not value:
            self.__multiplier = UnitMultiplier(value)
    @property
    def unit(self) -> 'UnitSymbol':
        return self.__unit
    @unit.setter
    def unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__unit = None
        elif not hasattr(self, 'unit') or self.unit is not value:
            self.__unit = UnitSymbol(value)
    @property
    def value(self) -> Decimal:
        return self.__value
    @value.setter
    def value(self, value: Decimal):
        if value == None:
            self.__value = None
        elif not hasattr(self, 'value') or self.value is not value:
            self.__value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Length', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Length.multiplier')
            prop.text = self.multiplier.value
        if self.unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Length.unit')
            prop.text = self.unit.value
        if self.value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Length.value')
            prop.text = str(self.value)
        return root
    def validate(self):
        if not isinstance(self.multiplier, UnitMultiplier):
            raise ValueError(f'Incorrect datatype in multiplier [Length] (expected UnitMultiplier but encountered {self.multiplier.__class__.__name__} instead)')
        if not isinstance(self.unit, UnitSymbol):
            raise ValueError(f'Incorrect datatype in unit [Length] (expected UnitSymbol but encountered {self.unit.__class__.__name__} instead)')
        if not isinstance(self.value, Decimal):
            raise ValueError(f'Incorrect datatype in value [Length] (expected Decimal but encountered {self.value.__class__.__name__} instead)')
 
class OperationalLimit():
    """A value associated with a specific kind of limit. 
The sub class value attribute shall be positive. 
The sub class value attribute is inversely proportional to OperationalLimitType.acceptableDuration (acceptableDuration for short). A pair of value_x and acceptableDuration_x are related to each other as follows:
if value_1 &gt; value_2 &gt; value_3 &gt;... then
acceptableDuration_1 &lt; acceptableDuration_2 &lt; acceptableDuration_3 &lt; ...
A value_x with direction="high" shall be greater than a value_y with direction="low"."""
    def __init__(self):
        self.URI = '#' + str(uuid())
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}OperationalLimit', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        return root
    def validate(self):
        pass
 
class OperationalLimitSet(IdentifiedObject):
    """A set of limits associated with equipment.  Sets of limits might apply to a specific temperature, or season for example. A set of limits may contain different severities of limit levels that would apply to the same equipment. The set may contain limits of different types such as apparent power and current limits or high and low voltage limits  that are logically applied together as a set."""
    def __init__(self, OperationalLimitValue: List['OperationalLimit'] = None, mRID: str = None, name: str = None):
        super().__init__(mRID=mRID, name=name)
        self.OperationalLimitValue = OperationalLimitValue
    def add_OperationalLimitValue(self, value: 'OperationalLimit'):
        if not hasattr(self, 'OperationalLimitValue'):
            self.__OperationalLimitValue = []
        if value not in self.__OperationalLimitValue:
            self.__OperationalLimitValue.append(value)
    @property
    def OperationalLimitValue(self) -> List['OperationalLimit']:
        return self.__OperationalLimitValue
    @OperationalLimitValue.setter
    def OperationalLimitValue(self, list_objs: List['OperationalLimit']):
        if list_objs == None:
            self.__OperationalLimitValue = []
            return
        for obj in list_objs:
            self.add_OperationalLimitValue(obj)
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}OperationalLimitSet' 
        if self.OperationalLimitValue != []:
            for item in self.OperationalLimitValue:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}OperationalLimitSet.OperationalLimitValue', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        return root
    def validate(self):
        super().validate()
        minBound, maxBound = 1, float('Inf')
        if len(self.OperationalLimitValue) < minBound or len(self.OperationalLimitValue) > maxBound:
            raise ValueError('Incorrect multiplicity in OperationalLimitValue [OperationalLimitSet]')
        if any(not isinstance(item, OperationalLimit) for item in self.OperationalLimitValue):
            raise ValueError(f'Incorrect datatype in OperationalLimitValue [OperationalLimitSet] (expected OperationalLimit but encountered {self.OperationalLimitValue.__class__.__name__} instead)')
 
class PerLengthSequenceImpedance(IdentifiedObject):
    """Sequence impedance and admittance parameters per unit length, for transposed lines of 1, 2, or 3 phases. For 1-phase lines, define x=x0=xself. For 2-phase lines, define x=xs-xm and x0=xs+xm."""
    def __init__(self, b0ch: 'SusceptancePerLength' = None, bch: 'SusceptancePerLength' = None, g0ch: 'ConductancePerLength' = None, gch: 'ConductancePerLength' = None, r: 'ResistancePerLength' = None, r0: 'ResistancePerLength' = None, x: 'ReactancePerLength' = None, x0: 'ReactancePerLength' = None, mRID: str = None, name: str = None):
        super().__init__(mRID=mRID, name=name)
        # Zero sequence shunt (charging) susceptance, per unit of length. 
        self.b0ch = b0ch
        # Positive sequence shunt (charging) susceptance, per unit of length. 
        self.bch = bch
        # Zero sequence shunt (charging) conductance, per unit of length. 
        self.g0ch = g0ch
        # Positive sequence shunt (charging) conductance, per unit of length. 
        self.gch = gch
        # Positive sequence series resistance, per unit of length. 
        self.r = r
        # Zero sequence series resistance, per unit of length. 
        self.r0 = r0
        # Positive sequence series reactance, per unit of length. 
        self.x = x
        # Zero sequence series reactance, per unit of length. 
        self.x0 = x0
    @property
    def b0ch(self) -> 'SusceptancePerLength':
        return self.__b0ch
    @b0ch.setter
    def b0ch(self, value: 'SusceptancePerLength'):
        if value == None:
            self.__b0ch = None
        elif not hasattr(self, 'b0ch') or self.b0ch is not value:
            self.__b0ch = value
    @property
    def bch(self) -> 'SusceptancePerLength':
        return self.__bch
    @bch.setter
    def bch(self, value: 'SusceptancePerLength'):
        if value == None:
            self.__bch = None
        elif not hasattr(self, 'bch') or self.bch is not value:
            self.__bch = value
    @property
    def g0ch(self) -> 'ConductancePerLength':
        return self.__g0ch
    @g0ch.setter
    def g0ch(self, value: 'ConductancePerLength'):
        if value == None:
            self.__g0ch = None
        elif not hasattr(self, 'g0ch') or self.g0ch is not value:
            self.__g0ch = value
    @property
    def gch(self) -> 'ConductancePerLength':
        return self.__gch
    @gch.setter
    def gch(self, value: 'ConductancePerLength'):
        if value == None:
            self.__gch = None
        elif not hasattr(self, 'gch') or self.gch is not value:
            self.__gch = value
    @property
    def r(self) -> 'ResistancePerLength':
        return self.__r
    @r.setter
    def r(self, value: 'ResistancePerLength'):
        if value == None:
            self.__r = None
        elif not hasattr(self, 'r') or self.r is not value:
            self.__r = value
    @property
    def r0(self) -> 'ResistancePerLength':
        return self.__r0
    @r0.setter
    def r0(self, value: 'ResistancePerLength'):
        if value == None:
            self.__r0 = None
        elif not hasattr(self, 'r0') or self.r0 is not value:
            self.__r0 = value
    @property
    def x(self) -> 'ReactancePerLength':
        return self.__x
    @x.setter
    def x(self, value: 'ReactancePerLength'):
        if value == None:
            self.__x = None
        elif not hasattr(self, 'x') or self.x is not value:
            self.__x = value
    @property
    def x0(self) -> 'ReactancePerLength':
        return self.__x0
    @x0.setter
    def x0(self, value: 'ReactancePerLength'):
        if value == None:
            self.__x0 = None
        elif not hasattr(self, 'x0') or self.x0 is not value:
            self.__x0 = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}PerLengthSequenceImpedance' 
        if self.b0ch != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PerLengthSequenceImpedance.b0ch', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__b0ch.URI})
        if self.bch != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PerLengthSequenceImpedance.bch', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__bch.URI})
        if self.g0ch != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PerLengthSequenceImpedance.g0ch', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__g0ch.URI})
        if self.gch != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PerLengthSequenceImpedance.gch', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__gch.URI})
        if self.r != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PerLengthSequenceImpedance.r', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__r.URI})
        if self.r0 != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PerLengthSequenceImpedance.r0', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__r0.URI})
        if self.x != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PerLengthSequenceImpedance.x', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__x.URI})
        if self.x0 != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PerLengthSequenceImpedance.x0', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__x0.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.b0ch, SusceptancePerLength) and self.b0ch != None:
            raise ValueError(f'Incorrect datatype in b0ch [PerLengthSequenceImpedance] (expected SusceptancePerLength but encountered {self.b0ch.__class__.__name__} instead)')
        if not isinstance(self.bch, SusceptancePerLength) and self.bch != None:
            raise ValueError(f'Incorrect datatype in bch [PerLengthSequenceImpedance] (expected SusceptancePerLength but encountered {self.bch.__class__.__name__} instead)')
        if not isinstance(self.g0ch, ConductancePerLength) and self.g0ch != None:
            raise ValueError(f'Incorrect datatype in g0ch [PerLengthSequenceImpedance] (expected ConductancePerLength but encountered {self.g0ch.__class__.__name__} instead)')
        if not isinstance(self.gch, ConductancePerLength) and self.gch != None:
            raise ValueError(f'Incorrect datatype in gch [PerLengthSequenceImpedance] (expected ConductancePerLength but encountered {self.gch.__class__.__name__} instead)')
        if not isinstance(self.r, ResistancePerLength) and self.r != None:
            raise ValueError(f'Incorrect datatype in r [PerLengthSequenceImpedance] (expected ResistancePerLength but encountered {self.r.__class__.__name__} instead)')
        if not isinstance(self.r0, ResistancePerLength) and self.r0 != None:
            raise ValueError(f'Incorrect datatype in r0 [PerLengthSequenceImpedance] (expected ResistancePerLength but encountered {self.r0.__class__.__name__} instead)')
        if not isinstance(self.x, ReactancePerLength) and self.x != None:
            raise ValueError(f'Incorrect datatype in x [PerLengthSequenceImpedance] (expected ReactancePerLength but encountered {self.x.__class__.__name__} instead)')
        if not isinstance(self.x0, ReactancePerLength) and self.x0 != None:
            raise ValueError(f'Incorrect datatype in x0 [PerLengthSequenceImpedance] (expected ReactancePerLength but encountered {self.x0.__class__.__name__} instead)')
 
class PowerSystemResource(IdentifiedObject):
    """A power system resource can be an item of equipment such as a switch, an equipment container containing many individual items of equipment such as a substation, or an organisational entity such as sub-control area. Power system resources can have measurements associated."""
    def __init__(self, mRID: str = None, name: str = None):
        super().__init__(mRID=mRID, name=name)
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}PowerSystemResource' 
        return root
    def validate(self):
        super().validate()
 
class PowerTransformerEnd():
    """A PowerTransformerEnd is associated with each Terminal of a PowerTransformer.
The impedance values r, r0, x, and x0 of a PowerTransformerEnd represents a star equivalent as follows
1) for a two Terminal PowerTransformer the high voltage (TransformerEnd.endNumber=1) PowerTransformerEnd has non zero values on r, r0, x, and x0 while the low voltage (TransformerEnd.endNumber=0) PowerTransformerEnd has zero values for r, r0, x, and x0.
2) for a three Terminal PowerTransformer the three PowerTransformerEnds represents a star equivalent with each leg in the star represented by r, r0, x, and x0 values.
3) For a three Terminal transformer each PowerTransformerEnd shall have g, g0, b and b0 values corresponding the no load losses distributed on the three PowerTransformerEnds. The total no load loss shunt impedances may also be placed at one of the PowerTransformerEnds, preferably the end numbered 1, having the shunt values on end 1 is the preferred way.
4) for a PowerTransformer with more than three Terminals the PowerTransformerEnd impedance values cannot be used. Instead use the TransformerMeshImpedance or split the transformer into multiple PowerTransformers."""
    def __init__(self, PowerTransformer: 'PowerTransformer' = None, connectionKind: 'WindingConnection' = None, endNumber: int = None, r: 'Resistance' = None, r0: 'Resistance' = None, ratedS: 'ApparentPower' = None, ratedU: 'Voltage' = None, x: 'Reactance' = None, x0: 'Reactance' = None):
        self.URI = '#' + str(uuid())
        # The power transformer of this power transformer end. 
        self.PowerTransformer = PowerTransformer
        # Kind of connection. 
        self.connectionKind = connectionKind
        # Number for this transformer end, corresponding to the end's order in the power transformer vector group or phase angle clock number.  Highest voltage winding should be 1.  Each end within a power transformer should have a unique subsequent end number.   Note the transformer end number need not match the terminal sequence number. 
        self.endNumber = endNumber
        # Resistance (star-model) of the transformer end. The attribute shall be equal or greater than zero for non-equivalent transformers. 
        self.r = r
        # Zero sequence series resistance (star-model) of the transformer end. 
        self.r0 = r0
        # Normal apparent power rating. The attribute shall be a positive value. For a two-winding transformer the values for the high and low voltage sides shall be identical. 
        self.ratedS = ratedS
        # Rated voltage: phase-phase for three-phase windings, and either phase-phase or phase-neutral for single-phase windings. A high voltage side, as given by TransformerEnd.endNumber, shall have a ratedU that is greater or equal than ratedU for the lower voltage sides. 
        self.ratedU = ratedU
        # Positive sequence series reactance (star-model) of the transformer end. 
        self.x = x
        # Zero sequence series reactance of the transformer end. 
        self.x0 = x0
    @property
    def PowerTransformer(self) -> 'PowerTransformer':
        return self.__PowerTransformer
    @PowerTransformer.setter
    def PowerTransformer(self, value: 'PowerTransformer'):
        if value == None:
            self.__PowerTransformer = None
        elif not hasattr(self, 'PowerTransformer') or self.PowerTransformer is not value:
            self.__PowerTransformer = value
            if isinstance(value.PowerTransformerEnd, list):
                value.add_PowerTransformerEnd(self)
            else:
                value.PowerTransformerEnd = self
    @property
    def connectionKind(self) -> 'WindingConnection':
        return self.__connectionKind
    @connectionKind.setter
    def connectionKind(self, value: 'WindingConnection'):
        if value == None:
            self.__connectionKind = None
        elif not hasattr(self, 'connectionKind') or self.connectionKind is not value:
            self.__connectionKind = WindingConnection(value)
    @property
    def endNumber(self) -> int:
        return self.__endNumber
    @endNumber.setter
    def endNumber(self, value: int):
        if value == None:
            self.__endNumber = None
        elif not hasattr(self, 'endNumber') or self.endNumber is not value:
            self.__endNumber = int(value)
    @property
    def r(self) -> 'Resistance':
        return self.__r
    @r.setter
    def r(self, value: 'Resistance'):
        if value == None:
            self.__r = None
        elif not hasattr(self, 'r') or self.r is not value:
            self.__r = value
    @property
    def r0(self) -> 'Resistance':
        return self.__r0
    @r0.setter
    def r0(self, value: 'Resistance'):
        if value == None:
            self.__r0 = None
        elif not hasattr(self, 'r0') or self.r0 is not value:
            self.__r0 = value
    @property
    def ratedS(self) -> 'ApparentPower':
        return self.__ratedS
    @ratedS.setter
    def ratedS(self, value: 'ApparentPower'):
        if value == None:
            self.__ratedS = None
        elif not hasattr(self, 'ratedS') or self.ratedS is not value:
            self.__ratedS = value
    @property
    def ratedU(self) -> 'Voltage':
        return self.__ratedU
    @ratedU.setter
    def ratedU(self, value: 'Voltage'):
        if value == None:
            self.__ratedU = None
        elif not hasattr(self, 'ratedU') or self.ratedU is not value:
            self.__ratedU = value
    @property
    def x(self) -> 'Reactance':
        return self.__x
    @x.setter
    def x(self, value: 'Reactance'):
        if value == None:
            self.__x = None
        elif not hasattr(self, 'x') or self.x is not value:
            self.__x = value
    @property
    def x0(self) -> 'Reactance':
        return self.__x0
    @x0.setter
    def x0(self, value: 'Reactance'):
        if value == None:
            self.__x0 = None
        elif not hasattr(self, 'x0') or self.x0 is not value:
            self.__x0 = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.PowerTransformer != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.PowerTransformer', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PowerTransformer.URI})
        if self.connectionKind != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.connectionKind')
            prop.text = self.connectionKind.value
        if self.endNumber != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.endNumber')
            prop.text = str(self.endNumber)
        if self.r != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.r', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__r.URI})
        if self.r0 != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.r0', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__r0.URI})
        if self.ratedS != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.ratedS', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__ratedS.URI})
        if self.ratedU != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.ratedU', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__ratedU.URI})
        if self.x != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.x', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__x.URI})
        if self.x0 != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.x0', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__x0.URI})
        return root
    def validate(self):
        if not isinstance(self.PowerTransformer, PowerTransformer):
            raise ValueError(f'Incorrect datatype in PowerTransformer [PowerTransformerEnd] (expected PowerTransformer but encountered {self.PowerTransformer.__class__.__name__} instead)')
        if not isinstance(self.connectionKind, WindingConnection) and self.connectionKind != None:
            raise ValueError(f'Incorrect datatype in connectionKind [PowerTransformerEnd] (expected WindingConnection but encountered {self.connectionKind.__class__.__name__} instead)')
        if not isinstance(self.endNumber, int):
            raise ValueError(f'Incorrect datatype in endNumber [PowerTransformerEnd] (expected int but encountered {self.endNumber.__class__.__name__} instead)')
        if not isinstance(self.r, Resistance) and self.r != None:
            raise ValueError(f'Incorrect datatype in r [PowerTransformerEnd] (expected Resistance but encountered {self.r.__class__.__name__} instead)')
        if not isinstance(self.r0, Resistance) and self.r0 != None:
            raise ValueError(f'Incorrect datatype in r0 [PowerTransformerEnd] (expected Resistance but encountered {self.r0.__class__.__name__} instead)')
        if not isinstance(self.ratedS, ApparentPower):
            raise ValueError(f'Incorrect datatype in ratedS [PowerTransformerEnd] (expected ApparentPower but encountered {self.ratedS.__class__.__name__} instead)')
        if not isinstance(self.ratedU, Voltage):
            raise ValueError(f'Incorrect datatype in ratedU [PowerTransformerEnd] (expected Voltage but encountered {self.ratedU.__class__.__name__} instead)')
        if not isinstance(self.x, Reactance) and self.x != None:
            raise ValueError(f'Incorrect datatype in x [PowerTransformerEnd] (expected Reactance but encountered {self.x.__class__.__name__} instead)')
        if not isinstance(self.x0, Reactance) and self.x0 != None:
            raise ValueError(f'Incorrect datatype in x0 [PowerTransformerEnd] (expected Reactance but encountered {self.x0.__class__.__name__} instead)')
 
class Reactance():
    """Reactance (imaginary part of impedance), at rated frequency."""
    def __init__(self, multiplier: 'UnitMultiplier' = None, unit: 'UnitSymbol' = None, value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.multiplier = multiplier
        self.unit = unit
        self.value = value
    @property
    def multiplier(self) -> 'UnitMultiplier':
        return self.__multiplier
    @multiplier.setter
    def multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__multiplier = None
        elif not hasattr(self, 'multiplier') or self.multiplier is not value:
            self.__multiplier = UnitMultiplier(value)
    @property
    def unit(self) -> 'UnitSymbol':
        return self.__unit
    @unit.setter
    def unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__unit = None
        elif not hasattr(self, 'unit') or self.unit is not value:
            self.__unit = UnitSymbol(value)
    @property
    def value(self) -> Decimal:
        return self.__value
    @value.setter
    def value(self, value: Decimal):
        if value == None:
            self.__value = None
        elif not hasattr(self, 'value') or self.value is not value:
            self.__value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Reactance', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Reactance.multiplier')
            prop.text = self.multiplier.value
        if self.unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Reactance.unit')
            prop.text = self.unit.value
        if self.value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Reactance.value')
            prop.text = str(self.value)
        return root
    def validate(self):
        if not isinstance(self.multiplier, UnitMultiplier):
            raise ValueError(f'Incorrect datatype in multiplier [Reactance] (expected UnitMultiplier but encountered {self.multiplier.__class__.__name__} instead)')
        if not isinstance(self.unit, UnitSymbol):
            raise ValueError(f'Incorrect datatype in unit [Reactance] (expected UnitSymbol but encountered {self.unit.__class__.__name__} instead)')
        if not isinstance(self.value, Decimal):
            raise ValueError(f'Incorrect datatype in value [Reactance] (expected Decimal but encountered {self.value.__class__.__name__} instead)')
 
class ReactancePerLength():
    """Reactance (imaginary part of impedance) per unit of length, at rated frequency."""
    def __init__(self, multiplier: 'UnitMultiplier' = None, unit: 'UnitSymbol' = None, value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.multiplier = multiplier
        self.unit = unit
        self.value = value
    @property
    def multiplier(self) -> 'UnitMultiplier':
        return self.__multiplier
    @multiplier.setter
    def multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__multiplier = None
        elif not hasattr(self, 'multiplier') or self.multiplier is not value:
            self.__multiplier = UnitMultiplier(value)
    @property
    def unit(self) -> 'UnitSymbol':
        return self.__unit
    @unit.setter
    def unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__unit = None
        elif not hasattr(self, 'unit') or self.unit is not value:
            self.__unit = UnitSymbol(value)
    @property
    def value(self) -> Decimal:
        return self.__value
    @value.setter
    def value(self, value: Decimal):
        if value == None:
            self.__value = None
        elif not hasattr(self, 'value') or self.value is not value:
            self.__value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}ReactancePerLength', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ReactancePerLength.multiplier')
            prop.text = self.multiplier.value
        if self.unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ReactancePerLength.unit')
            prop.text = self.unit.value
        if self.value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ReactancePerLength.value')
            prop.text = str(self.value)
        return root
    def validate(self):
        if not isinstance(self.multiplier, UnitMultiplier) and self.multiplier != None:
            raise ValueError(f'Incorrect datatype in multiplier [ReactancePerLength] (expected UnitMultiplier but encountered {self.multiplier.__class__.__name__} instead)')
        if not isinstance(self.unit, UnitSymbol) and self.unit != None:
            raise ValueError(f'Incorrect datatype in unit [ReactancePerLength] (expected UnitSymbol but encountered {self.unit.__class__.__name__} instead)')
        if not isinstance(self.value, Decimal) and self.value != None:
            raise ValueError(f'Incorrect datatype in value [ReactancePerLength] (expected Decimal but encountered {self.value.__class__.__name__} instead)')
 
class ReactivePower():
    """Product of RMS value of the voltage and the RMS value of the quadrature component of the current."""
    def __init__(self, multiplier: 'UnitMultiplier' = None, unit: 'UnitSymbol' = None, value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.multiplier = multiplier
        self.unit = unit
        self.value = value
    @property
    def multiplier(self) -> 'UnitMultiplier':
        return self.__multiplier
    @multiplier.setter
    def multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__multiplier = None
        elif not hasattr(self, 'multiplier') or self.multiplier is not value:
            self.__multiplier = UnitMultiplier(value)
    @property
    def unit(self) -> 'UnitSymbol':
        return self.__unit
    @unit.setter
    def unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__unit = None
        elif not hasattr(self, 'unit') or self.unit is not value:
            self.__unit = UnitSymbol(value)
    @property
    def value(self) -> Decimal:
        return self.__value
    @value.setter
    def value(self, value: Decimal):
        if value == None:
            self.__value = None
        elif not hasattr(self, 'value') or self.value is not value:
            self.__value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}ReactivePower', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ReactivePower.multiplier')
            prop.text = self.multiplier.value
        if self.unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ReactivePower.unit')
            prop.text = self.unit.value
        if self.value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ReactivePower.value')
            prop.text = str(self.value)
        return root
    def validate(self):
        if not isinstance(self.multiplier, UnitMultiplier):
            raise ValueError(f'Incorrect datatype in multiplier [ReactivePower] (expected UnitMultiplier but encountered {self.multiplier.__class__.__name__} instead)')
        if not isinstance(self.unit, UnitSymbol):
            raise ValueError(f'Incorrect datatype in unit [ReactivePower] (expected UnitSymbol but encountered {self.unit.__class__.__name__} instead)')
        if not isinstance(self.value, Decimal):
            raise ValueError(f'Incorrect datatype in value [ReactivePower] (expected Decimal but encountered {self.value.__class__.__name__} instead)')
 
class Resistance():
    """Resistance (real part of impedance)."""
    def __init__(self, multiplier: 'UnitMultiplier' = None, unit: 'UnitSymbol' = None, value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.multiplier = multiplier
        self.unit = unit
        self.value = value
    @property
    def multiplier(self) -> 'UnitMultiplier':
        return self.__multiplier
    @multiplier.setter
    def multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__multiplier = None
        elif not hasattr(self, 'multiplier') or self.multiplier is not value:
            self.__multiplier = UnitMultiplier(value)
    @property
    def unit(self) -> 'UnitSymbol':
        return self.__unit
    @unit.setter
    def unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__unit = None
        elif not hasattr(self, 'unit') or self.unit is not value:
            self.__unit = UnitSymbol(value)
    @property
    def value(self) -> Decimal:
        return self.__value
    @value.setter
    def value(self, value: Decimal):
        if value == None:
            self.__value = None
        elif not hasattr(self, 'value') or self.value is not value:
            self.__value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Resistance', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Resistance.multiplier')
            prop.text = self.multiplier.value
        if self.unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Resistance.unit')
            prop.text = self.unit.value
        if self.value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Resistance.value')
            prop.text = str(self.value)
        return root
    def validate(self):
        if not isinstance(self.multiplier, UnitMultiplier):
            raise ValueError(f'Incorrect datatype in multiplier [Resistance] (expected UnitMultiplier but encountered {self.multiplier.__class__.__name__} instead)')
        if not isinstance(self.unit, UnitSymbol):
            raise ValueError(f'Incorrect datatype in unit [Resistance] (expected UnitSymbol but encountered {self.unit.__class__.__name__} instead)')
        if not isinstance(self.value, Decimal):
            raise ValueError(f'Incorrect datatype in value [Resistance] (expected Decimal but encountered {self.value.__class__.__name__} instead)')
 
class ResistancePerLength():
    """Resistance (real part of impedance) per unit of length."""
    def __init__(self, multiplier: 'UnitMultiplier' = None, unit: 'UnitSymbol' = None, value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.multiplier = multiplier
        self.unit = unit
        self.value = value
    @property
    def multiplier(self) -> 'UnitMultiplier':
        return self.__multiplier
    @multiplier.setter
    def multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__multiplier = None
        elif not hasattr(self, 'multiplier') or self.multiplier is not value:
            self.__multiplier = UnitMultiplier(value)
    @property
    def unit(self) -> 'UnitSymbol':
        return self.__unit
    @unit.setter
    def unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__unit = None
        elif not hasattr(self, 'unit') or self.unit is not value:
            self.__unit = UnitSymbol(value)
    @property
    def value(self) -> Decimal:
        return self.__value
    @value.setter
    def value(self, value: Decimal):
        if value == None:
            self.__value = None
        elif not hasattr(self, 'value') or self.value is not value:
            self.__value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}ResistancePerLength', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ResistancePerLength.multiplier')
            prop.text = self.multiplier.value
        if self.unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ResistancePerLength.unit')
            prop.text = self.unit.value
        if self.value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ResistancePerLength.value')
            prop.text = str(self.value)
        return root
    def validate(self):
        if not isinstance(self.multiplier, UnitMultiplier) and self.multiplier != None:
            raise ValueError(f'Incorrect datatype in multiplier [ResistancePerLength] (expected UnitMultiplier but encountered {self.multiplier.__class__.__name__} instead)')
        if not isinstance(self.unit, UnitSymbol) and self.unit != None:
            raise ValueError(f'Incorrect datatype in unit [ResistancePerLength] (expected UnitSymbol but encountered {self.unit.__class__.__name__} instead)')
        if not isinstance(self.value, Decimal):
            raise ValueError(f'Incorrect datatype in value [ResistancePerLength] (expected Decimal but encountered {self.value.__class__.__name__} instead)')
 
class Susceptance():
    """Imaginary part of admittance."""
    def __init__(self, multiplier: 'UnitMultiplier' = None, unit: 'UnitSymbol' = None, value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.multiplier = multiplier
        self.unit = unit
        self.value = value
    @property
    def multiplier(self) -> 'UnitMultiplier':
        return self.__multiplier
    @multiplier.setter
    def multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__multiplier = None
        elif not hasattr(self, 'multiplier') or self.multiplier is not value:
            self.__multiplier = UnitMultiplier(value)
    @property
    def unit(self) -> 'UnitSymbol':
        return self.__unit
    @unit.setter
    def unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__unit = None
        elif not hasattr(self, 'unit') or self.unit is not value:
            self.__unit = UnitSymbol(value)
    @property
    def value(self) -> Decimal:
        return self.__value
    @value.setter
    def value(self, value: Decimal):
        if value == None:
            self.__value = None
        elif not hasattr(self, 'value') or self.value is not value:
            self.__value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Susceptance', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Susceptance.multiplier')
            prop.text = self.multiplier.value
        if self.unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Susceptance.unit')
            prop.text = self.unit.value
        if self.value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Susceptance.value')
            prop.text = str(self.value)
        return root
    def validate(self):
        if not isinstance(self.multiplier, UnitMultiplier):
            raise ValueError(f'Incorrect datatype in multiplier [Susceptance] (expected UnitMultiplier but encountered {self.multiplier.__class__.__name__} instead)')
        if not isinstance(self.unit, UnitSymbol):
            raise ValueError(f'Incorrect datatype in unit [Susceptance] (expected UnitSymbol but encountered {self.unit.__class__.__name__} instead)')
        if not isinstance(self.value, Decimal):
            raise ValueError(f'Incorrect datatype in value [Susceptance] (expected Decimal but encountered {self.value.__class__.__name__} instead)')
 
class SusceptancePerLength():
    """Imaginary part of admittance per unit of length."""
    def __init__(self, multiplier: 'UnitMultiplier' = None, unit: 'UnitSymbol' = None, value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.multiplier = multiplier
        self.unit = unit
        self.value = value
    @property
    def multiplier(self) -> 'UnitMultiplier':
        return self.__multiplier
    @multiplier.setter
    def multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__multiplier = None
        elif not hasattr(self, 'multiplier') or self.multiplier is not value:
            self.__multiplier = UnitMultiplier(value)
    @property
    def unit(self) -> 'UnitSymbol':
        return self.__unit
    @unit.setter
    def unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__unit = None
        elif not hasattr(self, 'unit') or self.unit is not value:
            self.__unit = UnitSymbol(value)
    @property
    def value(self) -> Decimal:
        return self.__value
    @value.setter
    def value(self, value: Decimal):
        if value == None:
            self.__value = None
        elif not hasattr(self, 'value') or self.value is not value:
            self.__value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}SusceptancePerLength', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}SusceptancePerLength.multiplier')
            prop.text = self.multiplier.value
        if self.unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}SusceptancePerLength.unit')
            prop.text = self.unit.value
        if self.value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}SusceptancePerLength.value')
            prop.text = str(self.value)
        return root
    def validate(self):
        if not isinstance(self.multiplier, UnitMultiplier) and self.multiplier != None:
            raise ValueError(f'Incorrect datatype in multiplier [SusceptancePerLength] (expected UnitMultiplier but encountered {self.multiplier.__class__.__name__} instead)')
        if not isinstance(self.unit, UnitSymbol) and self.unit != None:
            raise ValueError(f'Incorrect datatype in unit [SusceptancePerLength] (expected UnitSymbol but encountered {self.unit.__class__.__name__} instead)')
        if not isinstance(self.value, Decimal):
            raise ValueError(f'Incorrect datatype in value [SusceptancePerLength] (expected Decimal but encountered {self.value.__class__.__name__} instead)')
 
class Terminal():
    """An AC electrical connection point to a piece of conducting equipment. Terminals are connected at physical connection points called connectivity nodes."""
    def __init__(self, ConductingEquipment: 'ConductingEquipment' = None, ConnectivityNode: 'ConnectivityNode' = None, sequenceNumber: int = None):
        self.URI = '#' + str(uuid())
        # The conducting equipment of the terminal.  Conducting equipment have  terminals that may be connected to other conducting equipment terminals via connectivity nodes or topological nodes. 
        self.ConductingEquipment = ConductingEquipment
        # The connectivity node to which this terminal connects with zero impedance. 
        self.ConnectivityNode = ConnectivityNode
        # The orientation of the terminal connections for a multiple terminal conducting equipment.  The sequence numbering starts with 1 and additional terminals should follow in increasing order.   The first terminal is the "starting point" for a two terminal branch. 
        self.sequenceNumber = sequenceNumber
    @property
    def ConductingEquipment(self) -> 'ConductingEquipment':
        return self.__ConductingEquipment
    @ConductingEquipment.setter
    def ConductingEquipment(self, value: 'ConductingEquipment'):
        if value == None:
            self.__ConductingEquipment = None
        elif not hasattr(self, 'ConductingEquipment') or self.ConductingEquipment is not value:
            self.__ConductingEquipment = value
            if isinstance(value.Terminals, list):
                value.add_Terminals(self)
            else:
                value.Terminals = self
    @property
    def ConnectivityNode(self) -> 'ConnectivityNode':
        return self.__ConnectivityNode
    @ConnectivityNode.setter
    def ConnectivityNode(self, value: 'ConnectivityNode'):
        if value == None:
            self.__ConnectivityNode = None
        elif not hasattr(self, 'ConnectivityNode') or self.ConnectivityNode is not value:
            self.__ConnectivityNode = value
            if isinstance(value.Terminals, list):
                value.add_Terminals(self)
            else:
                value.Terminals = self
    @property
    def sequenceNumber(self) -> int:
        return self.__sequenceNumber
    @sequenceNumber.setter
    def sequenceNumber(self, value: int):
        if value == None:
            self.__sequenceNumber = None
        elif not hasattr(self, 'sequenceNumber') or self.sequenceNumber is not value:
            self.__sequenceNumber = int(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Terminal', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.ConductingEquipment != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Terminal.ConductingEquipment', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__ConductingEquipment.URI})
        if self.ConnectivityNode != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Terminal.ConnectivityNode', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__ConnectivityNode.URI})
        if self.sequenceNumber != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Terminal.sequenceNumber')
            prop.text = str(self.sequenceNumber)
        return root
    def validate(self):
        if not isinstance(self.ConductingEquipment, ConductingEquipment):
            raise ValueError(f'Incorrect datatype in ConductingEquipment [Terminal] (expected ConductingEquipment but encountered {self.ConductingEquipment.__class__.__name__} instead)')
        if not isinstance(self.ConnectivityNode, ConnectivityNode) and self.ConnectivityNode != None:
            raise ValueError(f'Incorrect datatype in ConnectivityNode [Terminal] (expected ConnectivityNode but encountered {self.ConnectivityNode.__class__.__name__} instead)')
        if not isinstance(self.sequenceNumber, int) and self.sequenceNumber != None:
            raise ValueError(f'Incorrect datatype in sequenceNumber [Terminal] (expected int but encountered {self.sequenceNumber.__class__.__name__} instead)')
 
class TopologicalNode(IdentifiedObject):
    """For a detailed substation model a topological node is a set of connectivity nodes that, in the current network state, are connected together through any type of closed switches, including  jumpers. Topological nodes change as the current network state changes (i.e., switches, breakers, etc. change state).
For a planning model, switch statuses are not used to form topological nodes. Instead they are manually created or deleted in a model builder tool. Topological nodes maintained this way are also called "busses"."""
    def __init__(self, ConnectivityNodeContainer: 'ConnectivityNodeContainer' = None, ConnectivityNodes: List['ConnectivityNode'] = None, pInjection: 'ActivePower' = None, qInjection: 'ReactivePower' = None, mRID: str = None, name: str = None):
        super().__init__(mRID=mRID, name=name)
        # The connectivity node container to which the toplogical node belongs. 
        self.ConnectivityNodeContainer = ConnectivityNodeContainer
        # The connectivity nodes combine together to form this topological node.  May depend on the current state of switches in the network. 
        self.ConnectivityNodes = ConnectivityNodes
        # The active power injected into the bus at this location in addition to injections from equipment.  Positive sign means injection into the TopologicalNode (bus). Starting value for a steady state solution. 
        self.pInjection = pInjection
        # The reactive power injected into the bus at this location in addition to injections from equipment. Positive sign means injection into the TopologicalNode (bus). Starting value for a steady state solution. 
        self.qInjection = qInjection
    @property
    def ConnectivityNodeContainer(self) -> 'ConnectivityNodeContainer':
        return self.__ConnectivityNodeContainer
    @ConnectivityNodeContainer.setter
    def ConnectivityNodeContainer(self, value: 'ConnectivityNodeContainer'):
        if value == None:
            self.__ConnectivityNodeContainer = None
        elif not hasattr(self, 'ConnectivityNodeContainer') or self.ConnectivityNodeContainer is not value:
            self.__ConnectivityNodeContainer = value
            if isinstance(value.TopologicalNode, list):
                value.add_TopologicalNode(self)
            else:
                value.TopologicalNode = self
    def add_ConnectivityNodes(self, value: 'ConnectivityNode'):
        if not hasattr(self, 'ConnectivityNodes'):
            self.__ConnectivityNodes = []
        if value not in self.__ConnectivityNodes:
            self.__ConnectivityNodes.append(value)
            if isinstance(value.TopologicalNode, list):
                value.add_TopologicalNode(self)
            else:
                value.TopologicalNode = self
    @property
    def ConnectivityNodes(self) -> List['ConnectivityNode']:
        return self.__ConnectivityNodes
    @ConnectivityNodes.setter
    def ConnectivityNodes(self, list_objs: List['ConnectivityNode']):
        if list_objs == None:
            self.__ConnectivityNodes = []
            return
        for obj in list_objs:
            self.add_ConnectivityNodes(obj)
        if len(list_objs):
            if isinstance(list_objs[0].TopologicalNode, list):
                for obj in list_objs:
                    obj.add_TopologicalNode(self)
            else:
                for obj in list_objs:
                    obj.TopologicalNode = self
    @property
    def pInjection(self) -> 'ActivePower':
        return self.__pInjection
    @pInjection.setter
    def pInjection(self, value: 'ActivePower'):
        if value == None:
            self.__pInjection = None
        elif not hasattr(self, 'pInjection') or self.pInjection is not value:
            self.__pInjection = value
    @property
    def qInjection(self) -> 'ReactivePower':
        return self.__qInjection
    @qInjection.setter
    def qInjection(self, value: 'ReactivePower'):
        if value == None:
            self.__qInjection = None
        elif not hasattr(self, 'qInjection') or self.qInjection is not value:
            self.__qInjection = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}TopologicalNode' 
        if self.ConnectivityNodeContainer != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}TopologicalNode.ConnectivityNodeContainer', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__ConnectivityNodeContainer.URI})
        if self.ConnectivityNodes != []:
            for item in self.ConnectivityNodes:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}TopologicalNode.ConnectivityNodes', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        if self.pInjection != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}TopologicalNode.pInjection', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__pInjection.URI})
        if self.qInjection != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}TopologicalNode.qInjection', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__qInjection.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.ConnectivityNodeContainer, ConnectivityNodeContainer) and self.ConnectivityNodeContainer != None:
            raise ValueError(f'Incorrect datatype in ConnectivityNodeContainer [TopologicalNode] (expected ConnectivityNodeContainer but encountered {self.ConnectivityNodeContainer.__class__.__name__} instead)')
        minBound, maxBound = 0, float('Inf')
        if len(self.ConnectivityNodes) < minBound or len(self.ConnectivityNodes) > maxBound:
            raise ValueError('Incorrect multiplicity in ConnectivityNodes [TopologicalNode]')
        if any(not isinstance(item, ConnectivityNode) for item in self.ConnectivityNodes):
            raise ValueError(f'Incorrect datatype in ConnectivityNodes [TopologicalNode] (expected ConnectivityNode but encountered {self.ConnectivityNodes.__class__.__name__} instead)')
        if not isinstance(self.pInjection, ActivePower) and self.pInjection != None:
            raise ValueError(f'Incorrect datatype in pInjection [TopologicalNode] (expected ActivePower but encountered {self.pInjection.__class__.__name__} instead)')
        if not isinstance(self.qInjection, ReactivePower) and self.qInjection != None:
            raise ValueError(f'Incorrect datatype in qInjection [TopologicalNode] (expected ReactivePower but encountered {self.qInjection.__class__.__name__} instead)')
 
class Voltage():
    """Electrical voltage, can be both AC and DC."""
    def __init__(self, multiplier: 'UnitMultiplier' = None, unit: 'UnitSymbol' = None, value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.multiplier = multiplier
        self.unit = unit
        self.value = value
    @property
    def multiplier(self) -> 'UnitMultiplier':
        return self.__multiplier
    @multiplier.setter
    def multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__multiplier = None
        elif not hasattr(self, 'multiplier') or self.multiplier is not value:
            self.__multiplier = UnitMultiplier(value)
    @property
    def unit(self) -> 'UnitSymbol':
        return self.__unit
    @unit.setter
    def unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__unit = None
        elif not hasattr(self, 'unit') or self.unit is not value:
            self.__unit = UnitSymbol(value)
    @property
    def value(self) -> Decimal:
        return self.__value
    @value.setter
    def value(self, value: Decimal):
        if value == None:
            self.__value = None
        elif not hasattr(self, 'value') or self.value is not value:
            self.__value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Voltage', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Voltage.multiplier')
            prop.text = self.multiplier.value
        if self.unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Voltage.unit')
            prop.text = self.unit.value
        if self.value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Voltage.value')
            prop.text = str(self.value)
        return root
    def validate(self):
        if not isinstance(self.multiplier, UnitMultiplier) and self.multiplier != None:
            raise ValueError(f'Incorrect datatype in multiplier [Voltage] (expected UnitMultiplier but encountered {self.multiplier.__class__.__name__} instead)')
        if not isinstance(self.unit, UnitSymbol) and self.unit != None:
            raise ValueError(f'Incorrect datatype in unit [Voltage] (expected UnitSymbol but encountered {self.unit.__class__.__name__} instead)')
        if not isinstance(self.value, Decimal) and self.value != None:
            raise ValueError(f'Incorrect datatype in value [Voltage] (expected Decimal but encountered {self.value.__class__.__name__} instead)')
 
class ActivePowerLimit(OperationalLimit):
    """Limit on active power flow."""
    def __init__(self, value: 'ActivePower' = None):
        super().__init__()
        # Value of active power limit. 
        self.value = value
    @property
    def value(self) -> 'ActivePower':
        return self.__value
    @value.setter
    def value(self, value: 'ActivePower'):
        if value == None:
            self.__value = None
        elif not hasattr(self, 'value') or self.value is not value:
            self.__value = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}ActivePowerLimit' 
        if self.value != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ActivePowerLimit.value', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__value.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.value, ActivePower):
            raise ValueError(f'Incorrect datatype in value [ActivePowerLimit] (expected ActivePower but encountered {self.value.__class__.__name__} instead)')
 
class ApparentPowerLimit(OperationalLimit):
    """Apparent power limit."""
    def __init__(self, value: 'ApparentPower' = None):
        super().__init__()
        # The apparent power limit. 
        self.value = value
    @property
    def value(self) -> 'ApparentPower':
        return self.__value
    @value.setter
    def value(self, value: 'ApparentPower'):
        if value == None:
            self.__value = None
        elif not hasattr(self, 'value') or self.value is not value:
            self.__value = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}ApparentPowerLimit' 
        if self.value != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ApparentPowerLimit.value', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__value.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.value, ApparentPower):
            raise ValueError(f'Incorrect datatype in value [ApparentPowerLimit] (expected ApparentPower but encountered {self.value.__class__.__name__} instead)')
 
class ConnectivityNode(IdentifiedObject):
    """Connectivity nodes are points where terminals of AC conducting equipment are connected together with zero impedance."""
    def __init__(self, Terminals: List['Terminal'] = None, TopologicalNode: 'TopologicalNode' = None, mRID: str = None, name: str = None):
        super().__init__(mRID=mRID, name=name)
        # Terminals interconnected with zero impedance at a this connectivity node. 
        self.Terminals = Terminals
        # The topological node to which this connectivity node is assigned.  May depend on the current state of switches in the network. 
        self.TopologicalNode = TopologicalNode
    def add_Terminals(self, value: 'Terminal'):
        if not hasattr(self, 'Terminals'):
            self.__Terminals = []
        if value not in self.__Terminals:
            self.__Terminals.append(value)
            if isinstance(value.ConnectivityNode, list):
                value.add_ConnectivityNode(self)
            else:
                value.ConnectivityNode = self
    @property
    def Terminals(self) -> List['Terminal']:
        return self.__Terminals
    @Terminals.setter
    def Terminals(self, list_objs: List['Terminal']):
        if list_objs == None:
            self.__Terminals = []
            return
        for obj in list_objs:
            self.add_Terminals(obj)
        if len(list_objs):
            if isinstance(list_objs[0].ConnectivityNode, list):
                for obj in list_objs:
                    obj.add_ConnectivityNode(self)
            else:
                for obj in list_objs:
                    obj.ConnectivityNode = self
    @property
    def TopologicalNode(self) -> 'TopologicalNode':
        return self.__TopologicalNode
    @TopologicalNode.setter
    def TopologicalNode(self, value: 'TopologicalNode'):
        if value == None:
            self.__TopologicalNode = None
        elif not hasattr(self, 'TopologicalNode') or self.TopologicalNode is not value:
            self.__TopologicalNode = value
            if isinstance(value.ConnectivityNodes, list):
                value.add_ConnectivityNodes(self)
            else:
                value.ConnectivityNodes = self
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}ConnectivityNode' 
        if self.Terminals != []:
            for item in self.Terminals:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ConnectivityNode.Terminals', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        if self.TopologicalNode != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ConnectivityNode.TopologicalNode', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__TopologicalNode.URI})
        return root
    def validate(self):
        super().validate()
        minBound, maxBound = 0, float('Inf')
        if len(self.Terminals) < minBound or len(self.Terminals) > maxBound:
            raise ValueError('Incorrect multiplicity in Terminals [ConnectivityNode]')
        if any(not isinstance(item, Terminal) for item in self.Terminals):
            raise ValueError(f'Incorrect datatype in Terminals [ConnectivityNode] (expected Terminal but encountered {self.Terminals.__class__.__name__} instead)')
        if not isinstance(self.TopologicalNode, TopologicalNode) and self.TopologicalNode != None:
            raise ValueError(f'Incorrect datatype in TopologicalNode [ConnectivityNode] (expected TopologicalNode but encountered {self.TopologicalNode.__class__.__name__} instead)')
 
class ConnectivityNodeContainer(PowerSystemResource):
    """A base class for all objects that may contain connectivity nodes or topological nodes."""
    def __init__(self, TopologicalNode: List['TopologicalNode'] = None, mRID: str = None, name: str = None):
        super().__init__(mRID=mRID, name=name)
        # The topological nodes which belong to this connectivity node container. 
        self.TopologicalNode = TopologicalNode
    def add_TopologicalNode(self, value: 'TopologicalNode'):
        if not hasattr(self, 'TopologicalNode'):
            self.__TopologicalNode = []
        if value not in self.__TopologicalNode:
            self.__TopologicalNode.append(value)
            if isinstance(value.ConnectivityNodeContainer, list):
                value.add_ConnectivityNodeContainer(self)
            else:
                value.ConnectivityNodeContainer = self
    @property
    def TopologicalNode(self) -> List['TopologicalNode']:
        return self.__TopologicalNode
    @TopologicalNode.setter
    def TopologicalNode(self, list_objs: List['TopologicalNode']):
        if list_objs == None:
            self.__TopologicalNode = []
            return
        for obj in list_objs:
            self.add_TopologicalNode(obj)
        if len(list_objs):
            if isinstance(list_objs[0].ConnectivityNodeContainer, list):
                for obj in list_objs:
                    obj.add_ConnectivityNodeContainer(self)
            else:
                for obj in list_objs:
                    obj.ConnectivityNodeContainer = self
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}ConnectivityNodeContainer' 
        if self.TopologicalNode != []:
            for item in self.TopologicalNode:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ConnectivityNodeContainer.TopologicalNode', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        return root
    def validate(self):
        super().validate()
        minBound, maxBound = 0, float('Inf')
        if len(self.TopologicalNode) < minBound or len(self.TopologicalNode) > maxBound:
            raise ValueError('Incorrect multiplicity in TopologicalNode [ConnectivityNodeContainer]')
        if any(not isinstance(item, TopologicalNode) for item in self.TopologicalNode):
            raise ValueError(f'Incorrect datatype in TopologicalNode [ConnectivityNodeContainer] (expected TopologicalNode but encountered {self.TopologicalNode.__class__.__name__} instead)')
 
class CurrentLimit(OperationalLimit):
    """Operational limit on current."""
    def __init__(self, value: 'CurrentFlow' = None):
        super().__init__()
        # Limit on current flow. 
        self.value = value
    @property
    def value(self) -> 'CurrentFlow':
        return self.__value
    @value.setter
    def value(self, value: 'CurrentFlow'):
        if value == None:
            self.__value = None
        elif not hasattr(self, 'value') or self.value is not value:
            self.__value = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}CurrentLimit' 
        if self.value != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}CurrentLimit.value', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__value.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.value, CurrentFlow):
            raise ValueError(f'Incorrect datatype in value [CurrentLimit] (expected CurrentFlow but encountered {self.value.__class__.__name__} instead)')
 
class Equipment(PowerSystemResource):
    """The parts of a power system that are physical devices, electronic or mechanical."""
    def __init__(self, EquipmentContainer: 'EquipmentContainer' = None, OperationalLimitSet: List['OperationalLimitSet'] = None, mRID: str = None, name: str = None):
        super().__init__(mRID=mRID, name=name)
        # Container of this equipment. 
        self.EquipmentContainer = EquipmentContainer
        # The operational limit sets associated with this equipment. 
        self.OperationalLimitSet = OperationalLimitSet
    @property
    def EquipmentContainer(self) -> 'EquipmentContainer':
        return self.__EquipmentContainer
    @EquipmentContainer.setter
    def EquipmentContainer(self, value: 'EquipmentContainer'):
        if value == None:
            self.__EquipmentContainer = None
        elif not hasattr(self, 'EquipmentContainer') or self.EquipmentContainer is not value:
            self.__EquipmentContainer = value
            if isinstance(value.Equipments, list):
                value.add_Equipments(self)
            else:
                value.Equipments = self
    def add_OperationalLimitSet(self, value: 'OperationalLimitSet'):
        if not hasattr(self, 'OperationalLimitSet'):
            self.__OperationalLimitSet = []
        if value not in self.__OperationalLimitSet:
            self.__OperationalLimitSet.append(value)
    @property
    def OperationalLimitSet(self) -> List['OperationalLimitSet']:
        return self.__OperationalLimitSet
    @OperationalLimitSet.setter
    def OperationalLimitSet(self, list_objs: List['OperationalLimitSet']):
        if list_objs == None:
            self.__OperationalLimitSet = []
            return
        for obj in list_objs:
            self.add_OperationalLimitSet(obj)
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}Equipment' 
        if self.EquipmentContainer != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Equipment.EquipmentContainer', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__EquipmentContainer.URI})
        if self.OperationalLimitSet != []:
            for item in self.OperationalLimitSet:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Equipment.OperationalLimitSet', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.EquipmentContainer, EquipmentContainer) and self.EquipmentContainer != None:
            raise ValueError(f'Incorrect datatype in EquipmentContainer [Equipment] (expected EquipmentContainer but encountered {self.EquipmentContainer.__class__.__name__} instead)')
        minBound, maxBound = 0, float('Inf')
        if len(self.OperationalLimitSet) < minBound or len(self.OperationalLimitSet) > maxBound:
            raise ValueError('Incorrect multiplicity in OperationalLimitSet [Equipment]')
        if any(not isinstance(item, OperationalLimitSet) for item in self.OperationalLimitSet):
            raise ValueError(f'Incorrect datatype in OperationalLimitSet [Equipment] (expected OperationalLimitSet but encountered {self.OperationalLimitSet.__class__.__name__} instead)')
 
class EquipmentContainer(PowerSystemResource):
    """A modeling construct to provide a root class for containing equipment."""
    def __init__(self, Equipments: List['Equipment'] = None, mRID: str = None, name: str = None):
        super().__init__(mRID=mRID, name=name)
        # Contained equipment. 
        self.Equipments = Equipments
    def add_Equipments(self, value: 'Equipment'):
        if not hasattr(self, 'Equipments'):
            self.__Equipments = []
        if value not in self.__Equipments:
            self.__Equipments.append(value)
            if isinstance(value.EquipmentContainer, list):
                value.add_EquipmentContainer(self)
            else:
                value.EquipmentContainer = self
    @property
    def Equipments(self) -> List['Equipment']:
        return self.__Equipments
    @Equipments.setter
    def Equipments(self, list_objs: List['Equipment']):
        if list_objs == None:
            self.__Equipments = []
            return
        for obj in list_objs:
            self.add_Equipments(obj)
        if len(list_objs):
            if isinstance(list_objs[0].EquipmentContainer, list):
                for obj in list_objs:
                    obj.add_EquipmentContainer(self)
            else:
                for obj in list_objs:
                    obj.EquipmentContainer = self
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}EquipmentContainer' 
        if self.Equipments != []:
            for item in self.Equipments:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EquipmentContainer.Equipments', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        return root
    def validate(self):
        super().validate()
        minBound, maxBound = 0, float('Inf')
        if len(self.Equipments) < minBound or len(self.Equipments) > maxBound:
            raise ValueError('Incorrect multiplicity in Equipments [EquipmentContainer]')
        if any(not isinstance(item, Equipment) for item in self.Equipments):
            raise ValueError(f'Incorrect datatype in Equipments [EquipmentContainer] (expected Equipment but encountered {self.Equipments.__class__.__name__} instead)')
 
class Feeder(ConnectivityNodeContainer):
    """"""
    def __init__(self, FeedingSubstation: 'Substation' = None, TopologicalNode: List['TopologicalNode'] = None, mRID: str = None, name: str = None):
        super().__init__(TopologicalNode=TopologicalNode, mRID=mRID, name=name)
        self.FeedingSubstation = FeedingSubstation
    @property
    def FeedingSubstation(self) -> 'Substation':
        return self.__FeedingSubstation
    @FeedingSubstation.setter
    def FeedingSubstation(self, value: 'Substation'):
        if value == None:
            self.__FeedingSubstation = None
        elif not hasattr(self, 'FeedingSubstation') or self.FeedingSubstation is not value:
            self.__FeedingSubstation = value
            if isinstance(value.SubstationFeeder, list):
                value.add_SubstationFeeder(self)
            else:
                value.SubstationFeeder = self
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}Feeder' 
        if self.FeedingSubstation != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Feeder.FeedingSubstation', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__FeedingSubstation.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.FeedingSubstation, Substation) and self.FeedingSubstation != None:
            raise ValueError(f'Incorrect datatype in FeedingSubstation [Feeder] (expected Substation but encountered {self.FeedingSubstation.__class__.__name__} instead)')
 
class Substation(EquipmentContainer):
    """A collection of equipment for purposes other than generation or utilization, through which electric energy in bulk is passed for the purposes of switching or modifying its characteristics."""
    def __init__(self, SubstationFeeder: List['Feeder'] = None, Equipments: List['Equipment'] = None, mRID: str = None, name: str = None):
        super().__init__(Equipments=Equipments, mRID=mRID, name=name)
        self.SubstationFeeder = SubstationFeeder
    def add_SubstationFeeder(self, value: 'Feeder'):
        if not hasattr(self, 'SubstationFeeder'):
            self.__SubstationFeeder = []
        if value not in self.__SubstationFeeder:
            self.__SubstationFeeder.append(value)
            if isinstance(value.FeedingSubstation, list):
                value.add_FeedingSubstation(self)
            else:
                value.FeedingSubstation = self
    @property
    def SubstationFeeder(self) -> List['Feeder']:
        return self.__SubstationFeeder
    @SubstationFeeder.setter
    def SubstationFeeder(self, list_objs: List['Feeder']):
        if list_objs == None:
            self.__SubstationFeeder = []
            return
        for obj in list_objs:
            self.add_SubstationFeeder(obj)
        if len(list_objs):
            if isinstance(list_objs[0].FeedingSubstation, list):
                for obj in list_objs:
                    obj.add_FeedingSubstation(self)
            else:
                for obj in list_objs:
                    obj.FeedingSubstation = self
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}Substation' 
        if self.SubstationFeeder != []:
            for item in self.SubstationFeeder:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Substation.SubstationFeeder', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        return root
    def validate(self):
        super().validate()
        minBound, maxBound = 0, float('Inf')
        if len(self.SubstationFeeder) < minBound or len(self.SubstationFeeder) > maxBound:
            raise ValueError('Incorrect multiplicity in SubstationFeeder [Substation]')
        if any(not isinstance(item, Feeder) for item in self.SubstationFeeder):
            raise ValueError(f'Incorrect datatype in SubstationFeeder [Substation] (expected Feeder but encountered {self.SubstationFeeder.__class__.__name__} instead)')
 
class ConductingEquipment(Equipment):
    """The parts of the AC power system that are designed to carry current or that are conductively connected through terminals."""
    def __init__(self, Terminals: List['Terminal'] = None, EquipmentContainer: 'EquipmentContainer' = None, OperationalLimitSet: List['OperationalLimitSet'] = None, mRID: str = None, name: str = None):
        super().__init__(EquipmentContainer=EquipmentContainer, OperationalLimitSet=OperationalLimitSet, mRID=mRID, name=name)
        # Conducting equipment have terminals that may be connected to other conducting equipment terminals via connectivity nodes or topological nodes. 
        self.Terminals = Terminals
    def add_Terminals(self, value: 'Terminal'):
        if not hasattr(self, 'Terminals'):
            self.__Terminals = []
        if value not in self.__Terminals:
            self.__Terminals.append(value)
            if isinstance(value.ConductingEquipment, list):
                value.add_ConductingEquipment(self)
            else:
                value.ConductingEquipment = self
    @property
    def Terminals(self) -> List['Terminal']:
        return self.__Terminals
    @Terminals.setter
    def Terminals(self, list_objs: List['Terminal']):
        if list_objs == None:
            self.__Terminals = []
            return
        for obj in list_objs:
            self.add_Terminals(obj)
        if len(list_objs):
            if isinstance(list_objs[0].ConductingEquipment, list):
                for obj in list_objs:
                    obj.add_ConductingEquipment(self)
            else:
                for obj in list_objs:
                    obj.ConductingEquipment = self
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}ConductingEquipment' 
        if self.Terminals != []:
            for item in self.Terminals:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ConductingEquipment.Terminals', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        return root
    def validate(self):
        super().validate()
        minBound, maxBound = 0, float('Inf')
        if len(self.Terminals) < minBound or len(self.Terminals) > maxBound:
            raise ValueError('Incorrect multiplicity in Terminals [ConductingEquipment]')
        if any(not isinstance(item, Terminal) for item in self.Terminals):
            raise ValueError(f'Incorrect datatype in Terminals [ConductingEquipment] (expected Terminal but encountered {self.Terminals.__class__.__name__} instead)')
 
class Conductor(ConductingEquipment):
    """Combination of conducting material with consistent electrical characteristics, building a single electrical system, used to carry current between points in the power system."""
    def __init__(self, length: 'Length' = None, Terminals: List['Terminal'] = None, EquipmentContainer: 'EquipmentContainer' = None, OperationalLimitSet: List['OperationalLimitSet'] = None, mRID: str = None, name: str = None):
        super().__init__(Terminals=Terminals, EquipmentContainer=EquipmentContainer, OperationalLimitSet=OperationalLimitSet, mRID=mRID, name=name)
        # Segment length for calculating line section capabilities 
        self.length = length
    @property
    def length(self) -> 'Length':
        return self.__length
    @length.setter
    def length(self, value: 'Length'):
        if value == None:
            self.__length = None
        elif not hasattr(self, 'length') or self.length is not value:
            self.__length = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}Conductor' 
        if self.length != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Conductor.length', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__length.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.length, Length):
            raise ValueError(f'Incorrect datatype in length [Conductor] (expected Length but encountered {self.length.__class__.__name__} instead)')
 
class EnergyConsumer(ConductingEquipment):
    """Generic user of energy - a  point of consumption on the power system model."""
    def __init__(self, p: 'ActivePower' = None, q: 'ReactivePower' = None, Terminals: List['Terminal'] = None, EquipmentContainer: 'EquipmentContainer' = None, OperationalLimitSet: List['OperationalLimitSet'] = None, mRID: str = None, name: str = None):
        super().__init__(Terminals=Terminals, EquipmentContainer=EquipmentContainer, OperationalLimitSet=OperationalLimitSet, mRID=mRID, name=name)
        # Active power of the load. Load sign convention is used, i.e. positive sign means flow out from a node. For voltage dependent loads the value is at rated voltage. Starting value for a steady state solution. 
        self.p = p
        # Reactive power of the load. Load sign convention is used, i.e. positive sign means flow out from a node. For voltage dependent loads the value is at rated voltage. Starting value for a steady state solution. 
        self.q = q
    @property
    def p(self) -> 'ActivePower':
        return self.__p
    @p.setter
    def p(self, value: 'ActivePower'):
        if value == None:
            self.__p = None
        elif not hasattr(self, 'p') or self.p is not value:
            self.__p = value
    @property
    def q(self) -> 'ReactivePower':
        return self.__q
    @q.setter
    def q(self, value: 'ReactivePower'):
        if value == None:
            self.__q = None
        elif not hasattr(self, 'q') or self.q is not value:
            self.__q = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}EnergyConsumer' 
        if self.p != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EnergyConsumer.p', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__p.URI})
        if self.q != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EnergyConsumer.q', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__q.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.p, ActivePower):
            raise ValueError(f'Incorrect datatype in p [EnergyConsumer] (expected ActivePower but encountered {self.p.__class__.__name__} instead)')
        if not isinstance(self.q, ReactivePower):
            raise ValueError(f'Incorrect datatype in q [EnergyConsumer] (expected ReactivePower but encountered {self.q.__class__.__name__} instead)')
 
class EquivalentInjection(ConductingEquipment):
    """This class represents equivalent injections (generation or load).  Voltage regulation is allowed only at the point of connection."""
    def __init__(self, BaseVoltage: 'BaseVoltage' = None, r: 'Resistance' = None, r0: 'Resistance' = None, x: 'Reactance' = None, x0: 'Reactance' = None, Terminals: List['Terminal'] = None, EquipmentContainer: 'EquipmentContainer' = None, OperationalLimitSet: List['OperationalLimitSet'] = None, mRID: str = None, name: str = None):
        super().__init__(Terminals=Terminals, EquipmentContainer=EquipmentContainer, OperationalLimitSet=OperationalLimitSet, mRID=mRID, name=name)
        # Base voltage of this conducting equipment.  Use only when there is no voltage level container used and only one base voltage applies.  For example, not used for transformers. 
        self.BaseVoltage = BaseVoltage
        # Positive sequence resistance. Used to represent Extended-Ward (IEC 60909). Usage : Extended-Ward is a result of network reduction prior to the data exchange. 
        self.r = r
        # Zero sequence resistance. Used to represent Extended-Ward (IEC 60909). Usage : Extended-Ward is a result of network reduction prior to the data exchange. 
        self.r0 = r0
        # Positive sequence reactance. Used to represent Extended-Ward (IEC 60909). Usage : Extended-Ward is a result of network reduction prior to the data exchange. 
        self.x = x
        # Zero sequence reactance. Used to represent Extended-Ward (IEC 60909). Usage : Extended-Ward is a result of network reduction prior to the data exchange. 
        self.x0 = x0
    @property
    def BaseVoltage(self) -> 'BaseVoltage':
        return self.__BaseVoltage
    @BaseVoltage.setter
    def BaseVoltage(self, value: 'BaseVoltage'):
        if value == None:
            self.__BaseVoltage = None
        elif not hasattr(self, 'BaseVoltage') or self.BaseVoltage is not value:
            self.__BaseVoltage = value
    @property
    def r(self) -> 'Resistance':
        return self.__r
    @r.setter
    def r(self, value: 'Resistance'):
        if value == None:
            self.__r = None
        elif not hasattr(self, 'r') or self.r is not value:
            self.__r = value
    @property
    def r0(self) -> 'Resistance':
        return self.__r0
    @r0.setter
    def r0(self, value: 'Resistance'):
        if value == None:
            self.__r0 = None
        elif not hasattr(self, 'r0') or self.r0 is not value:
            self.__r0 = value
    @property
    def x(self) -> 'Reactance':
        return self.__x
    @x.setter
    def x(self, value: 'Reactance'):
        if value == None:
            self.__x = None
        elif not hasattr(self, 'x') or self.x is not value:
            self.__x = value
    @property
    def x0(self) -> 'Reactance':
        return self.__x0
    @x0.setter
    def x0(self, value: 'Reactance'):
        if value == None:
            self.__x0 = None
        elif not hasattr(self, 'x0') or self.x0 is not value:
            self.__x0 = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}EquivalentInjection' 
        if self.BaseVoltage != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EquivalentInjection.BaseVoltage', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__BaseVoltage.URI})
        if self.r != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EquivalentInjection.r', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__r.URI})
        if self.r0 != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EquivalentInjection.r0', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__r0.URI})
        if self.x != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EquivalentInjection.x', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__x.URI})
        if self.x0 != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EquivalentInjection.x0', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__x0.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.BaseVoltage, BaseVoltage):
            raise ValueError(f'Incorrect datatype in BaseVoltage [EquivalentInjection] (expected BaseVoltage but encountered {self.BaseVoltage.__class__.__name__} instead)')
        if not isinstance(self.r, Resistance) and self.r != None:
            raise ValueError(f'Incorrect datatype in r [EquivalentInjection] (expected Resistance but encountered {self.r.__class__.__name__} instead)')
        if not isinstance(self.r0, Resistance) and self.r0 != None:
            raise ValueError(f'Incorrect datatype in r0 [EquivalentInjection] (expected Resistance but encountered {self.r0.__class__.__name__} instead)')
        if not isinstance(self.x, Reactance) and self.x != None:
            raise ValueError(f'Incorrect datatype in x [EquivalentInjection] (expected Reactance but encountered {self.x.__class__.__name__} instead)')
        if not isinstance(self.x0, Reactance) and self.x0 != None:
            raise ValueError(f'Incorrect datatype in x0 [EquivalentInjection] (expected Reactance but encountered {self.x0.__class__.__name__} instead)')
 
class PowerTransformer(ConductingEquipment):
    """An electrical device consisting of  two or more coupled windings, with or without a magnetic core, for introducing mutual coupling between electric circuits. Transformers can be used to control voltage and phase shift (active power flow).
A power transformer may be composed of separate transformer tanks that need not be identical.
A power transformer can be modeled with or without tanks and is intended for use in both balanced and unbalanced representations.   A power transformer typically has two terminals, but may have one (grounding), three or more terminals.
The inherited association ConductingEquipment.BaseVoltage should not be used.  The association from TransformerEnd to BaseVoltage should be used instead."""
    def __init__(self, PowerTransformerEnd: List['PowerTransformerEnd'] = None, Terminals: List['Terminal'] = None, EquipmentContainer: 'EquipmentContainer' = None, OperationalLimitSet: List['OperationalLimitSet'] = None, mRID: str = None, name: str = None):
        super().__init__(Terminals=Terminals, EquipmentContainer=EquipmentContainer, OperationalLimitSet=OperationalLimitSet, mRID=mRID, name=name)
        # The ends of this power transformer. 
        self.PowerTransformerEnd = PowerTransformerEnd
    def add_PowerTransformerEnd(self, value: 'PowerTransformerEnd'):
        if not hasattr(self, 'PowerTransformerEnd'):
            self.__PowerTransformerEnd = []
        if value not in self.__PowerTransformerEnd:
            self.__PowerTransformerEnd.append(value)
            if isinstance(value.PowerTransformer, list):
                value.add_PowerTransformer(self)
            else:
                value.PowerTransformer = self
    @property
    def PowerTransformerEnd(self) -> List['PowerTransformerEnd']:
        return self.__PowerTransformerEnd
    @PowerTransformerEnd.setter
    def PowerTransformerEnd(self, list_objs: List['PowerTransformerEnd']):
        if list_objs == None:
            self.__PowerTransformerEnd = []
            return
        for obj in list_objs:
            self.add_PowerTransformerEnd(obj)
        if len(list_objs):
            if isinstance(list_objs[0].PowerTransformer, list):
                for obj in list_objs:
                    obj.add_PowerTransformer(self)
            else:
                for obj in list_objs:
                    obj.PowerTransformer = self
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}PowerTransformer' 
        if self.PowerTransformerEnd != []:
            for item in self.PowerTransformerEnd:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformer.PowerTransformerEnd', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        return root
    def validate(self):
        super().validate()
        minBound, maxBound = 1, float('Inf')
        if len(self.PowerTransformerEnd) < minBound or len(self.PowerTransformerEnd) > maxBound:
            raise ValueError('Incorrect multiplicity in PowerTransformerEnd [PowerTransformer]')
        if any(not isinstance(item, PowerTransformerEnd) for item in self.PowerTransformerEnd):
            raise ValueError(f'Incorrect datatype in PowerTransformerEnd [PowerTransformer] (expected PowerTransformerEnd but encountered {self.PowerTransformerEnd.__class__.__name__} instead)')
 
class Switch(ConductingEquipment):
    """A generic device designed to close, or open, or both, one or more electric circuits.  All switches are two terminal devices including grounding switches."""
    def __init__(self, normalOpen: bool = None, open: bool = None, Terminals: List['Terminal'] = None, EquipmentContainer: 'EquipmentContainer' = None, OperationalLimitSet: List['OperationalLimitSet'] = None, mRID: str = None, name: str = None):
        super().__init__(Terminals=Terminals, EquipmentContainer=EquipmentContainer, OperationalLimitSet=OperationalLimitSet, mRID=mRID, name=name)
        # The attribute is used in cases when no Measurement for the status value is present. If the Switch has a status measurement the Discrete.normalValue is expected to match with the Switch.normalOpen. 
        self.normalOpen = normalOpen
        # The attribute tells if the switch is considered open when used as input to topology processing. 
        self.open = open
    @property
    def normalOpen(self) -> bool:
        return self.__normalOpen
    @normalOpen.setter
    def normalOpen(self, value: bool):
        if value == None:
            self.__normalOpen = None
        elif not hasattr(self, 'normalOpen') or self.normalOpen is not value:
            self.__normalOpen = str(value).lower() == 'true' 
    @property
    def open(self) -> bool:
        return self.__open
    @open.setter
    def open(self, value: bool):
        if value == None:
            self.__open = None
        elif not hasattr(self, 'open') or self.open is not value:
            self.__open = str(value).lower() == 'true' 
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}Switch' 
        if self.normalOpen != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Switch.normalOpen')
            prop.text = str(self.normalOpen).lower()
        if self.open != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Switch.open')
            prop.text = str(self.open).lower()
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.normalOpen, bool) and self.normalOpen != None:
            raise ValueError(f'Incorrect datatype in normalOpen [Switch] (expected bool but encountered {self.normalOpen.__class__.__name__} instead)')
        if not isinstance(self.open, bool) and self.open != None:
            raise ValueError(f'Incorrect datatype in open [Switch] (expected bool but encountered {self.open.__class__.__name__} instead)')
 
class ACLineSegment(Conductor):
    """A wire or combination of wires, with consistent electrical characteristics, building a single electrical system, used to carry alternating current between points in the power system.
For symmetrical, transposed 3ph lines, it is sufficient to use  attributes of the line segment, which describe impedances and admittances for the entire length of the segment.  Additionally impedances can be computed by using length and associated per length impedances.
The BaseVoltage at the two ends of ACLineSegments in a Line shall have the same BaseVoltage.nominalVoltage. However, boundary lines  may have slightly different BaseVoltage.nominalVoltages and  variation is allowed. Larger voltage difference in general requires use of an equivalent branch."""
    def __init__(self, PerLengthImpedance: 'PerLengthSequenceImpedance' = None, length: 'Length' = None, Terminals: List['Terminal'] = None, EquipmentContainer: 'EquipmentContainer' = None, OperationalLimitSet: List['OperationalLimitSet'] = None, mRID: str = None, name: str = None):
        super().__init__(length=length, Terminals=Terminals, EquipmentContainer=EquipmentContainer, OperationalLimitSet=OperationalLimitSet, mRID=mRID, name=name)
        # Per-length impedance of this line segment. 
        self.PerLengthImpedance = PerLengthImpedance
    @property
    def PerLengthImpedance(self) -> 'PerLengthSequenceImpedance':
        return self.__PerLengthImpedance
    @PerLengthImpedance.setter
    def PerLengthImpedance(self, value: 'PerLengthSequenceImpedance'):
        if value == None:
            self.__PerLengthImpedance = None
        elif not hasattr(self, 'PerLengthImpedance') or self.PerLengthImpedance is not value:
            self.__PerLengthImpedance = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}ACLineSegment' 
        if self.PerLengthImpedance != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ACLineSegment.PerLengthImpedance', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PerLengthImpedance.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.PerLengthImpedance, PerLengthSequenceImpedance) and self.PerLengthImpedance != None:
            raise ValueError(f'Incorrect datatype in PerLengthImpedance [ACLineSegment] (expected PerLengthSequenceImpedance but encountered {self.PerLengthImpedance.__class__.__name__} instead)')
 
class BusbarSection(ConductingEquipment):
    """A conductor, or group of conductors, with negligible impedance, that serve to connect other conducting equipment within a single substation. 
Voltage measurements are typically obtained from VoltageTransformers that are connected to busbar sections. A bus bar section may have many physical terminals but for analysis is modelled with exactly one logical terminal."""
    def __init__(self, ipMax: 'CurrentFlow' = None, Terminals: List['Terminal'] = None, EquipmentContainer: 'EquipmentContainer' = None, OperationalLimitSet: List['OperationalLimitSet'] = None, mRID: str = None, name: str = None):
        super().__init__(Terminals=Terminals, EquipmentContainer=EquipmentContainer, OperationalLimitSet=OperationalLimitSet, mRID=mRID, name=name)
        # Maximum allowable peak short-circuit current of busbar (Ipmax in the IEC 60909-0).  Mechanical limit of the busbar in the substation itself. Used for short circuit data exchange according to IEC 60909 
        self.ipMax = ipMax
    @property
    def ipMax(self) -> 'CurrentFlow':
        return self.__ipMax
    @ipMax.setter
    def ipMax(self, value: 'CurrentFlow'):
        if value == None:
            self.__ipMax = None
        elif not hasattr(self, 'ipMax') or self.ipMax is not value:
            self.__ipMax = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}BusbarSection' 
        if self.ipMax != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}BusbarSection.ipMax', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__ipMax.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.ipMax, CurrentFlow) and self.ipMax != None:
            raise ValueError(f'Incorrect datatype in ipMax [BusbarSection] (expected CurrentFlow but encountered {self.ipMax.__class__.__name__} instead)')

__all__ = [
    'DocumentCIMRDF',
    'ACLineSegment',
    'ActivePower',
    'ActivePowerLimit',
    'ApparentPower',
    'ApparentPowerLimit',
    'BaseVoltage',
    'BusbarSection',
    'Conductance',
    'ConductancePerLength',
    'ConductingEquipment',
    'Conductor',
    'ConnectivityNode',
    'ConnectivityNodeContainer',
    'CurrentFlow',
    'CurrentLimit',
    'EnergyConsumer',
    'Equipment',
    'EquipmentContainer',
    'EquivalentInjection',
    'Feeder',
    'IdentifiedObject',
    'Length',
    'OperationalLimit',
    'OperationalLimitSet',
    'PerLengthSequenceImpedance',
    'PhaseShuntConnectionKind',
    'PowerSystemResource',
    'PowerTransformer',
    'PowerTransformerEnd',
    'Reactance',
    'ReactancePerLength',
    'ReactivePower',
    'Resistance',
    'ResistancePerLength',
    'Substation',
    'Susceptance',
    'SusceptancePerLength',
    'Switch',
    'Terminal',
    'TopologicalNode',
    'UnitMultiplier',
    'UnitSymbol',
    'Voltage',
    'WindingConnection'
]
