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
            dtype = get_type(resource_item).replace('.', '_')
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
    def __init__(self, ActivePower_multiplier: 'UnitMultiplier' = None, ActivePower_unit: 'UnitSymbol' = None, ActivePower_value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.ActivePower_multiplier = ActivePower_multiplier
        self.ActivePower_unit = ActivePower_unit
        self.ActivePower_value = ActivePower_value
    @property
    def ActivePower_multiplier(self) -> 'UnitMultiplier':
        return self.__ActivePower_multiplier
    @ActivePower_multiplier.setter
    def ActivePower_multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__ActivePower_multiplier = None
        elif not hasattr(self, 'ActivePower_multiplier') or not self.ActivePower_multiplier is value:
            self.__ActivePower_multiplier = UnitMultiplier(value)
    @property
    def ActivePower_unit(self) -> 'UnitSymbol':
        return self.__ActivePower_unit
    @ActivePower_unit.setter
    def ActivePower_unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__ActivePower_unit = None
        elif not hasattr(self, 'ActivePower_unit') or not self.ActivePower_unit is value:
            self.__ActivePower_unit = UnitSymbol(value)
    @property
    def ActivePower_value(self) -> Decimal:
        return self.__ActivePower_value
    @ActivePower_value.setter
    def ActivePower_value(self, value: Decimal):
        if value == None:
            self.__ActivePower_value = None
        elif not hasattr(self, 'ActivePower_value') or not self.ActivePower_value is value:
            self.__ActivePower_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}ActivePower', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.ActivePower_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ActivePower.multiplier')
            prop.text = self.ActivePower_multiplier.value
        if self.ActivePower_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ActivePower.unit')
            prop.text = self.ActivePower_unit.value
        if self.ActivePower_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ActivePower.value')
            prop.text = str(self.ActivePower_value)
        return root
    def validate(self):
        if not isinstance(self.ActivePower_multiplier, UnitMultiplier):
            raise ValueError(f'Incorrect datatype in ActivePower_multiplier [ActivePower] (expected UnitMultiplier but encountered {self.ActivePower_multiplier.__class__.__name__} instead)')
        if not isinstance(self.ActivePower_unit, UnitSymbol):
            raise ValueError(f'Incorrect datatype in ActivePower_unit [ActivePower] (expected UnitSymbol but encountered {self.ActivePower_unit.__class__.__name__} instead)')
        if not isinstance(self.ActivePower_value, Decimal):
            raise ValueError(f'Incorrect datatype in ActivePower_value [ActivePower] (expected Decimal but encountered {self.ActivePower_value.__class__.__name__} instead)')
 
class ApparentPower():
    """Product of the RMS value of the voltage and the RMS value of the current."""
    def __init__(self, ApparentPower_multiplier: 'UnitMultiplier' = None, ApparentPower_unit: 'UnitSymbol' = None, ApparentPower_value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.ApparentPower_multiplier = ApparentPower_multiplier
        self.ApparentPower_unit = ApparentPower_unit
        self.ApparentPower_value = ApparentPower_value
    @property
    def ApparentPower_multiplier(self) -> 'UnitMultiplier':
        return self.__ApparentPower_multiplier
    @ApparentPower_multiplier.setter
    def ApparentPower_multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__ApparentPower_multiplier = None
        elif not hasattr(self, 'ApparentPower_multiplier') or not self.ApparentPower_multiplier is value:
            self.__ApparentPower_multiplier = UnitMultiplier(value)
    @property
    def ApparentPower_unit(self) -> 'UnitSymbol':
        return self.__ApparentPower_unit
    @ApparentPower_unit.setter
    def ApparentPower_unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__ApparentPower_unit = None
        elif not hasattr(self, 'ApparentPower_unit') or not self.ApparentPower_unit is value:
            self.__ApparentPower_unit = UnitSymbol(value)
    @property
    def ApparentPower_value(self) -> Decimal:
        return self.__ApparentPower_value
    @ApparentPower_value.setter
    def ApparentPower_value(self, value: Decimal):
        if value == None:
            self.__ApparentPower_value = None
        elif not hasattr(self, 'ApparentPower_value') or not self.ApparentPower_value is value:
            self.__ApparentPower_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}ApparentPower', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.ApparentPower_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ApparentPower.multiplier')
            prop.text = self.ApparentPower_multiplier.value
        if self.ApparentPower_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ApparentPower.unit')
            prop.text = self.ApparentPower_unit.value
        if self.ApparentPower_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ApparentPower.value')
            prop.text = str(self.ApparentPower_value)
        return root
    def validate(self):
        if not isinstance(self.ApparentPower_multiplier, UnitMultiplier) and self.ApparentPower_multiplier != None:
            raise ValueError(f'Incorrect datatype in ApparentPower_multiplier [ApparentPower] (expected UnitMultiplier but encountered {self.ApparentPower_multiplier.__class__.__name__} instead)')
        if not isinstance(self.ApparentPower_unit, UnitSymbol) and self.ApparentPower_unit != None:
            raise ValueError(f'Incorrect datatype in ApparentPower_unit [ApparentPower] (expected UnitSymbol but encountered {self.ApparentPower_unit.__class__.__name__} instead)')
        if not isinstance(self.ApparentPower_value, Decimal) and self.ApparentPower_value != None:
            raise ValueError(f'Incorrect datatype in ApparentPower_value [ApparentPower] (expected Decimal but encountered {self.ApparentPower_value.__class__.__name__} instead)')
 
class BaseVoltage():
    """Defines a system base voltage which is referenced."""
    def __init__(self, BaseVoltage_nominalVoltage: 'Voltage' = None):
        self.URI = '#' + str(uuid())
        # The power system resource's base voltage. 
        self.BaseVoltage_nominalVoltage = BaseVoltage_nominalVoltage
    @property
    def BaseVoltage_nominalVoltage(self) -> 'Voltage':
        return self.__BaseVoltage_nominalVoltage
    @BaseVoltage_nominalVoltage.setter
    def BaseVoltage_nominalVoltage(self, value: 'Voltage'):
        if value == None:
            self.__BaseVoltage_nominalVoltage = None
        elif not hasattr(self, 'BaseVoltage_nominalVoltage') or not self.BaseVoltage_nominalVoltage is value:
            self.__BaseVoltage_nominalVoltage = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}BaseVoltage', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.BaseVoltage_nominalVoltage != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}BaseVoltage.nominalVoltage', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__BaseVoltage_nominalVoltage.URI})
        return root
    def validate(self):
        if not isinstance(self.BaseVoltage_nominalVoltage, Voltage):
            raise ValueError(f'Incorrect datatype in BaseVoltage_nominalVoltage [BaseVoltage] (expected Voltage but encountered {self.BaseVoltage_nominalVoltage.__class__.__name__} instead)')
 
class Conductance():
    """Factor by which voltage must be multiplied to give corresponding power lost from a circuit. Real part of admittance."""
    def __init__(self, Conductance_multiplier: 'UnitMultiplier' = None, Conductance_unit: 'UnitSymbol' = None, Conductance_value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.Conductance_multiplier = Conductance_multiplier
        self.Conductance_unit = Conductance_unit
        self.Conductance_value = Conductance_value
    @property
    def Conductance_multiplier(self) -> 'UnitMultiplier':
        return self.__Conductance_multiplier
    @Conductance_multiplier.setter
    def Conductance_multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__Conductance_multiplier = None
        elif not hasattr(self, 'Conductance_multiplier') or not self.Conductance_multiplier is value:
            self.__Conductance_multiplier = UnitMultiplier(value)
    @property
    def Conductance_unit(self) -> 'UnitSymbol':
        return self.__Conductance_unit
    @Conductance_unit.setter
    def Conductance_unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__Conductance_unit = None
        elif not hasattr(self, 'Conductance_unit') or not self.Conductance_unit is value:
            self.__Conductance_unit = UnitSymbol(value)
    @property
    def Conductance_value(self) -> Decimal:
        return self.__Conductance_value
    @Conductance_value.setter
    def Conductance_value(self, value: Decimal):
        if value == None:
            self.__Conductance_value = None
        elif not hasattr(self, 'Conductance_value') or not self.Conductance_value is value:
            self.__Conductance_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Conductance', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.Conductance_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Conductance.multiplier')
            prop.text = self.Conductance_multiplier.value
        if self.Conductance_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Conductance.unit')
            prop.text = self.Conductance_unit.value
        if self.Conductance_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Conductance.value')
            prop.text = str(self.Conductance_value)
        return root
    def validate(self):
        if not isinstance(self.Conductance_multiplier, UnitMultiplier):
            raise ValueError(f'Incorrect datatype in Conductance_multiplier [Conductance] (expected UnitMultiplier but encountered {self.Conductance_multiplier.__class__.__name__} instead)')
        if not isinstance(self.Conductance_unit, UnitSymbol):
            raise ValueError(f'Incorrect datatype in Conductance_unit [Conductance] (expected UnitSymbol but encountered {self.Conductance_unit.__class__.__name__} instead)')
        if not isinstance(self.Conductance_value, Decimal):
            raise ValueError(f'Incorrect datatype in Conductance_value [Conductance] (expected Decimal but encountered {self.Conductance_value.__class__.__name__} instead)')
 
class ConductancePerLength():
    """Real part of admittance per unit of length."""
    def __init__(self, ConductancePerLength_multiplier: 'UnitMultiplier' = None, ConductancePerLength_unit: 'UnitSymbol' = None, ConductancePerLength_value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.ConductancePerLength_multiplier = ConductancePerLength_multiplier
        self.ConductancePerLength_unit = ConductancePerLength_unit
        self.ConductancePerLength_value = ConductancePerLength_value
    @property
    def ConductancePerLength_multiplier(self) -> 'UnitMultiplier':
        return self.__ConductancePerLength_multiplier
    @ConductancePerLength_multiplier.setter
    def ConductancePerLength_multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__ConductancePerLength_multiplier = None
        elif not hasattr(self, 'ConductancePerLength_multiplier') or not self.ConductancePerLength_multiplier is value:
            self.__ConductancePerLength_multiplier = UnitMultiplier(value)
    @property
    def ConductancePerLength_unit(self) -> 'UnitSymbol':
        return self.__ConductancePerLength_unit
    @ConductancePerLength_unit.setter
    def ConductancePerLength_unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__ConductancePerLength_unit = None
        elif not hasattr(self, 'ConductancePerLength_unit') or not self.ConductancePerLength_unit is value:
            self.__ConductancePerLength_unit = UnitSymbol(value)
    @property
    def ConductancePerLength_value(self) -> Decimal:
        return self.__ConductancePerLength_value
    @ConductancePerLength_value.setter
    def ConductancePerLength_value(self, value: Decimal):
        if value == None:
            self.__ConductancePerLength_value = None
        elif not hasattr(self, 'ConductancePerLength_value') or not self.ConductancePerLength_value is value:
            self.__ConductancePerLength_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}ConductancePerLength', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.ConductancePerLength_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ConductancePerLength.multiplier')
            prop.text = self.ConductancePerLength_multiplier.value
        if self.ConductancePerLength_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ConductancePerLength.unit')
            prop.text = self.ConductancePerLength_unit.value
        if self.ConductancePerLength_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ConductancePerLength.value')
            prop.text = str(self.ConductancePerLength_value)
        return root
    def validate(self):
        if not isinstance(self.ConductancePerLength_multiplier, UnitMultiplier) and self.ConductancePerLength_multiplier != None:
            raise ValueError(f'Incorrect datatype in ConductancePerLength_multiplier [ConductancePerLength] (expected UnitMultiplier but encountered {self.ConductancePerLength_multiplier.__class__.__name__} instead)')
        if not isinstance(self.ConductancePerLength_unit, UnitSymbol) and self.ConductancePerLength_unit != None:
            raise ValueError(f'Incorrect datatype in ConductancePerLength_unit [ConductancePerLength] (expected UnitSymbol but encountered {self.ConductancePerLength_unit.__class__.__name__} instead)')
        if not isinstance(self.ConductancePerLength_value, Decimal) and self.ConductancePerLength_value != None:
            raise ValueError(f'Incorrect datatype in ConductancePerLength_value [ConductancePerLength] (expected Decimal but encountered {self.ConductancePerLength_value.__class__.__name__} instead)')
 
class CurrentFlow():
    """Electrical current with sign convention: positive flow is out of the conducting equipment into the connectivity node. Can be both AC and DC."""
    def __init__(self, CurrentFlow_multiplier: 'UnitMultiplier' = None, CurrentFlow_unit: 'UnitSymbol' = None, CurrentFlow_value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.CurrentFlow_multiplier = CurrentFlow_multiplier
        self.CurrentFlow_unit = CurrentFlow_unit
        self.CurrentFlow_value = CurrentFlow_value
    @property
    def CurrentFlow_multiplier(self) -> 'UnitMultiplier':
        return self.__CurrentFlow_multiplier
    @CurrentFlow_multiplier.setter
    def CurrentFlow_multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__CurrentFlow_multiplier = None
        elif not hasattr(self, 'CurrentFlow_multiplier') or not self.CurrentFlow_multiplier is value:
            self.__CurrentFlow_multiplier = UnitMultiplier(value)
    @property
    def CurrentFlow_unit(self) -> 'UnitSymbol':
        return self.__CurrentFlow_unit
    @CurrentFlow_unit.setter
    def CurrentFlow_unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__CurrentFlow_unit = None
        elif not hasattr(self, 'CurrentFlow_unit') or not self.CurrentFlow_unit is value:
            self.__CurrentFlow_unit = UnitSymbol(value)
    @property
    def CurrentFlow_value(self) -> Decimal:
        return self.__CurrentFlow_value
    @CurrentFlow_value.setter
    def CurrentFlow_value(self, value: Decimal):
        if value == None:
            self.__CurrentFlow_value = None
        elif not hasattr(self, 'CurrentFlow_value') or not self.CurrentFlow_value is value:
            self.__CurrentFlow_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}CurrentFlow', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.CurrentFlow_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}CurrentFlow.multiplier')
            prop.text = self.CurrentFlow_multiplier.value
        if self.CurrentFlow_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}CurrentFlow.unit')
            prop.text = self.CurrentFlow_unit.value
        if self.CurrentFlow_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}CurrentFlow.value')
            prop.text = str(self.CurrentFlow_value)
        return root
    def validate(self):
        if not isinstance(self.CurrentFlow_multiplier, UnitMultiplier) and self.CurrentFlow_multiplier != None:
            raise ValueError(f'Incorrect datatype in CurrentFlow_multiplier [CurrentFlow] (expected UnitMultiplier but encountered {self.CurrentFlow_multiplier.__class__.__name__} instead)')
        if not isinstance(self.CurrentFlow_unit, UnitSymbol) and self.CurrentFlow_unit != None:
            raise ValueError(f'Incorrect datatype in CurrentFlow_unit [CurrentFlow] (expected UnitSymbol but encountered {self.CurrentFlow_unit.__class__.__name__} instead)')
        if not isinstance(self.CurrentFlow_value, Decimal) and self.CurrentFlow_value != None:
            raise ValueError(f'Incorrect datatype in CurrentFlow_value [CurrentFlow] (expected Decimal but encountered {self.CurrentFlow_value.__class__.__name__} instead)')
 
class IdentifiedObject():
    """This is a root class to provide common identification for all classes needing identification and naming attributes."""
    def __init__(self, IdentifiedObject_mRID: str = None, IdentifiedObject_name: str = None):
        self.URI = '#' + str(uuid())
        # Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID,  as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended. For CIMXML data files in RDF syntax conforming to IEC 61970-552 Edition 1, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements. 
        self.IdentifiedObject_mRID = IdentifiedObject_mRID
        # The name is any free human readable and possibly non unique text naming the object. 
        self.IdentifiedObject_name = IdentifiedObject_name
    @property
    def IdentifiedObject_mRID(self) -> str:
        return self.__IdentifiedObject_mRID
    @IdentifiedObject_mRID.setter
    def IdentifiedObject_mRID(self, value: str):
        if value == None:
            self.__IdentifiedObject_mRID = None
        elif not hasattr(self, 'IdentifiedObject_mRID') or not self.IdentifiedObject_mRID is value:
            self.__IdentifiedObject_mRID = str(value)
    @property
    def IdentifiedObject_name(self) -> str:
        return self.__IdentifiedObject_name
    @IdentifiedObject_name.setter
    def IdentifiedObject_name(self, value: str):
        if value == None:
            self.__IdentifiedObject_name = None
        elif not hasattr(self, 'IdentifiedObject_name') or not self.IdentifiedObject_name is value:
            self.__IdentifiedObject_name = str(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}IdentifiedObject', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.IdentifiedObject_mRID != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}IdentifiedObject.mRID')
            prop.text = str(self.IdentifiedObject_mRID)
        if self.IdentifiedObject_name != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}IdentifiedObject.name')
            prop.text = str(self.IdentifiedObject_name)
        return root
    def validate(self):
        if not isinstance(self.IdentifiedObject_mRID, str):
            raise ValueError(f'Incorrect datatype in IdentifiedObject_mRID [IdentifiedObject] (expected str but encountered {self.IdentifiedObject_mRID.__class__.__name__} instead)')
        if not isinstance(self.IdentifiedObject_name, str) and self.IdentifiedObject_name != None:
            raise ValueError(f'Incorrect datatype in IdentifiedObject_name [IdentifiedObject] (expected str but encountered {self.IdentifiedObject_name.__class__.__name__} instead)')
 
class Length():
    """Unit of length. Never negative."""
    def __init__(self, Length_multiplier: 'UnitMultiplier' = None, Length_unit: 'UnitSymbol' = None, Length_value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.Length_multiplier = Length_multiplier
        self.Length_unit = Length_unit
        self.Length_value = Length_value
    @property
    def Length_multiplier(self) -> 'UnitMultiplier':
        return self.__Length_multiplier
    @Length_multiplier.setter
    def Length_multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__Length_multiplier = None
        elif not hasattr(self, 'Length_multiplier') or not self.Length_multiplier is value:
            self.__Length_multiplier = UnitMultiplier(value)
    @property
    def Length_unit(self) -> 'UnitSymbol':
        return self.__Length_unit
    @Length_unit.setter
    def Length_unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__Length_unit = None
        elif not hasattr(self, 'Length_unit') or not self.Length_unit is value:
            self.__Length_unit = UnitSymbol(value)
    @property
    def Length_value(self) -> Decimal:
        return self.__Length_value
    @Length_value.setter
    def Length_value(self, value: Decimal):
        if value == None:
            self.__Length_value = None
        elif not hasattr(self, 'Length_value') or not self.Length_value is value:
            self.__Length_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Length', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.Length_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Length.multiplier')
            prop.text = self.Length_multiplier.value
        if self.Length_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Length.unit')
            prop.text = self.Length_unit.value
        if self.Length_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Length.value')
            prop.text = str(self.Length_value)
        return root
    def validate(self):
        if not isinstance(self.Length_multiplier, UnitMultiplier):
            raise ValueError(f'Incorrect datatype in Length_multiplier [Length] (expected UnitMultiplier but encountered {self.Length_multiplier.__class__.__name__} instead)')
        if not isinstance(self.Length_unit, UnitSymbol):
            raise ValueError(f'Incorrect datatype in Length_unit [Length] (expected UnitSymbol but encountered {self.Length_unit.__class__.__name__} instead)')
        if not isinstance(self.Length_value, Decimal):
            raise ValueError(f'Incorrect datatype in Length_value [Length] (expected Decimal but encountered {self.Length_value.__class__.__name__} instead)')
 
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
    def __init__(self, OperationalLimitSet_OperationalLimitValue: List['OperationalLimit'] = None, IdentifiedObject_mRID: str = None, IdentifiedObject_name: str = None):
        super().__init__(IdentifiedObject_mRID = IdentifiedObject_mRID, IdentifiedObject_name = IdentifiedObject_name, )
        self.OperationalLimitSet_OperationalLimitValue = OperationalLimitSet_OperationalLimitValue
    def add_OperationalLimitSet_OperationalLimitValue(self, value: 'OperationalLimit'):
        if not hasattr(self, 'OperationalLimitSet_OperationalLimitValue'):
            self.__OperationalLimitSet_OperationalLimitValue = []
        if value not in self.__OperationalLimitSet_OperationalLimitValue:
            self.__OperationalLimitSet_OperationalLimitValue.append(value)
    @property
    def OperationalLimitSet_OperationalLimitValue(self) -> List['OperationalLimit']:
        return self.__OperationalLimitSet_OperationalLimitValue
    @OperationalLimitSet_OperationalLimitValue.setter
    def OperationalLimitSet_OperationalLimitValue(self, list_objs: List['OperationalLimit']):
        if list_objs == None:
            self.__OperationalLimitSet_OperationalLimitValue = []
            return
        for obj in list_objs:
            self.add_OperationalLimitSet_OperationalLimitValue(obj)
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}OperationalLimitSet' 
        if self.OperationalLimitSet_OperationalLimitValue != []:
            for item in self.OperationalLimitSet_OperationalLimitValue:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}OperationalLimitSet.OperationalLimitValue', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        return root
    def validate(self):
        super().validate()
        minBound, maxBound = 1, float('Inf')
        if len(self.OperationalLimitSet_OperationalLimitValue) < minBound or len(self.OperationalLimitSet_OperationalLimitValue) > maxBound:
            raise ValueError('Incorrect multiplicity in OperationalLimitSet_OperationalLimitValue [OperationalLimitSet]')
        if any(not isinstance(item, OperationalLimit) for item in self.OperationalLimitSet_OperationalLimitValue):
            raise ValueError(f'Incorrect datatype in OperationalLimitSet_OperationalLimitValue [OperationalLimitSet] (expected OperationalLimit but encountered {self.OperationalLimitSet_OperationalLimitValue.__class__.__name__} instead)')
 
class PerLengthSequenceImpedance(IdentifiedObject):
    """Sequence impedance and admittance parameters per unit length, for transposed lines of 1, 2, or 3 phases. For 1-phase lines, define x=x0=xself. For 2-phase lines, define x=xs-xm and x0=xs+xm."""
    def __init__(self, PerLengthSequenceImpedance_b0ch: 'SusceptancePerLength' = None, PerLengthSequenceImpedance_bch: 'SusceptancePerLength' = None, PerLengthSequenceImpedance_g0ch: 'ConductancePerLength' = None, PerLengthSequenceImpedance_gch: 'ConductancePerLength' = None, PerLengthSequenceImpedance_r: 'ResistancePerLength' = None, PerLengthSequenceImpedance_r0: 'ResistancePerLength' = None, PerLengthSequenceImpedance_x: 'ReactancePerLength' = None, PerLengthSequenceImpedance_x0: 'ReactancePerLength' = None, IdentifiedObject_mRID: str = None, IdentifiedObject_name: str = None):
        super().__init__(IdentifiedObject_mRID = IdentifiedObject_mRID, IdentifiedObject_name = IdentifiedObject_name, )
        # Zero sequence shunt (charging) susceptance, per unit of length. 
        self.PerLengthSequenceImpedance_b0ch = PerLengthSequenceImpedance_b0ch
        # Positive sequence shunt (charging) susceptance, per unit of length. 
        self.PerLengthSequenceImpedance_bch = PerLengthSequenceImpedance_bch
        # Zero sequence shunt (charging) conductance, per unit of length. 
        self.PerLengthSequenceImpedance_g0ch = PerLengthSequenceImpedance_g0ch
        # Positive sequence shunt (charging) conductance, per unit of length. 
        self.PerLengthSequenceImpedance_gch = PerLengthSequenceImpedance_gch
        # Positive sequence series resistance, per unit of length. 
        self.PerLengthSequenceImpedance_r = PerLengthSequenceImpedance_r
        # Zero sequence series resistance, per unit of length. 
        self.PerLengthSequenceImpedance_r0 = PerLengthSequenceImpedance_r0
        # Positive sequence series reactance, per unit of length. 
        self.PerLengthSequenceImpedance_x = PerLengthSequenceImpedance_x
        # Zero sequence series reactance, per unit of length. 
        self.PerLengthSequenceImpedance_x0 = PerLengthSequenceImpedance_x0
    @property
    def PerLengthSequenceImpedance_b0ch(self) -> 'SusceptancePerLength':
        return self.__PerLengthSequenceImpedance_b0ch
    @PerLengthSequenceImpedance_b0ch.setter
    def PerLengthSequenceImpedance_b0ch(self, value: 'SusceptancePerLength'):
        if value == None:
            self.__PerLengthSequenceImpedance_b0ch = None
        elif not hasattr(self, 'PerLengthSequenceImpedance_b0ch') or not self.PerLengthSequenceImpedance_b0ch is value:
            self.__PerLengthSequenceImpedance_b0ch = value
    @property
    def PerLengthSequenceImpedance_bch(self) -> 'SusceptancePerLength':
        return self.__PerLengthSequenceImpedance_bch
    @PerLengthSequenceImpedance_bch.setter
    def PerLengthSequenceImpedance_bch(self, value: 'SusceptancePerLength'):
        if value == None:
            self.__PerLengthSequenceImpedance_bch = None
        elif not hasattr(self, 'PerLengthSequenceImpedance_bch') or not self.PerLengthSequenceImpedance_bch is value:
            self.__PerLengthSequenceImpedance_bch = value
    @property
    def PerLengthSequenceImpedance_g0ch(self) -> 'ConductancePerLength':
        return self.__PerLengthSequenceImpedance_g0ch
    @PerLengthSequenceImpedance_g0ch.setter
    def PerLengthSequenceImpedance_g0ch(self, value: 'ConductancePerLength'):
        if value == None:
            self.__PerLengthSequenceImpedance_g0ch = None
        elif not hasattr(self, 'PerLengthSequenceImpedance_g0ch') or not self.PerLengthSequenceImpedance_g0ch is value:
            self.__PerLengthSequenceImpedance_g0ch = value
    @property
    def PerLengthSequenceImpedance_gch(self) -> 'ConductancePerLength':
        return self.__PerLengthSequenceImpedance_gch
    @PerLengthSequenceImpedance_gch.setter
    def PerLengthSequenceImpedance_gch(self, value: 'ConductancePerLength'):
        if value == None:
            self.__PerLengthSequenceImpedance_gch = None
        elif not hasattr(self, 'PerLengthSequenceImpedance_gch') or not self.PerLengthSequenceImpedance_gch is value:
            self.__PerLengthSequenceImpedance_gch = value
    @property
    def PerLengthSequenceImpedance_r(self) -> 'ResistancePerLength':
        return self.__PerLengthSequenceImpedance_r
    @PerLengthSequenceImpedance_r.setter
    def PerLengthSequenceImpedance_r(self, value: 'ResistancePerLength'):
        if value == None:
            self.__PerLengthSequenceImpedance_r = None
        elif not hasattr(self, 'PerLengthSequenceImpedance_r') or not self.PerLengthSequenceImpedance_r is value:
            self.__PerLengthSequenceImpedance_r = value
    @property
    def PerLengthSequenceImpedance_r0(self) -> 'ResistancePerLength':
        return self.__PerLengthSequenceImpedance_r0
    @PerLengthSequenceImpedance_r0.setter
    def PerLengthSequenceImpedance_r0(self, value: 'ResistancePerLength'):
        if value == None:
            self.__PerLengthSequenceImpedance_r0 = None
        elif not hasattr(self, 'PerLengthSequenceImpedance_r0') or not self.PerLengthSequenceImpedance_r0 is value:
            self.__PerLengthSequenceImpedance_r0 = value
    @property
    def PerLengthSequenceImpedance_x(self) -> 'ReactancePerLength':
        return self.__PerLengthSequenceImpedance_x
    @PerLengthSequenceImpedance_x.setter
    def PerLengthSequenceImpedance_x(self, value: 'ReactancePerLength'):
        if value == None:
            self.__PerLengthSequenceImpedance_x = None
        elif not hasattr(self, 'PerLengthSequenceImpedance_x') or not self.PerLengthSequenceImpedance_x is value:
            self.__PerLengthSequenceImpedance_x = value
    @property
    def PerLengthSequenceImpedance_x0(self) -> 'ReactancePerLength':
        return self.__PerLengthSequenceImpedance_x0
    @PerLengthSequenceImpedance_x0.setter
    def PerLengthSequenceImpedance_x0(self, value: 'ReactancePerLength'):
        if value == None:
            self.__PerLengthSequenceImpedance_x0 = None
        elif not hasattr(self, 'PerLengthSequenceImpedance_x0') or not self.PerLengthSequenceImpedance_x0 is value:
            self.__PerLengthSequenceImpedance_x0 = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}PerLengthSequenceImpedance' 
        if self.PerLengthSequenceImpedance_b0ch != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PerLengthSequenceImpedance.b0ch', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PerLengthSequenceImpedance_b0ch.URI})
        if self.PerLengthSequenceImpedance_bch != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PerLengthSequenceImpedance.bch', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PerLengthSequenceImpedance_bch.URI})
        if self.PerLengthSequenceImpedance_g0ch != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PerLengthSequenceImpedance.g0ch', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PerLengthSequenceImpedance_g0ch.URI})
        if self.PerLengthSequenceImpedance_gch != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PerLengthSequenceImpedance.gch', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PerLengthSequenceImpedance_gch.URI})
        if self.PerLengthSequenceImpedance_r != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PerLengthSequenceImpedance.r', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PerLengthSequenceImpedance_r.URI})
        if self.PerLengthSequenceImpedance_r0 != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PerLengthSequenceImpedance.r0', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PerLengthSequenceImpedance_r0.URI})
        if self.PerLengthSequenceImpedance_x != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PerLengthSequenceImpedance.x', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PerLengthSequenceImpedance_x.URI})
        if self.PerLengthSequenceImpedance_x0 != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PerLengthSequenceImpedance.x0', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PerLengthSequenceImpedance_x0.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.PerLengthSequenceImpedance_b0ch, SusceptancePerLength) and self.PerLengthSequenceImpedance_b0ch != None:
            raise ValueError(f'Incorrect datatype in PerLengthSequenceImpedance_b0ch [PerLengthSequenceImpedance] (expected SusceptancePerLength but encountered {self.PerLengthSequenceImpedance_b0ch.__class__.__name__} instead)')
        if not isinstance(self.PerLengthSequenceImpedance_bch, SusceptancePerLength) and self.PerLengthSequenceImpedance_bch != None:
            raise ValueError(f'Incorrect datatype in PerLengthSequenceImpedance_bch [PerLengthSequenceImpedance] (expected SusceptancePerLength but encountered {self.PerLengthSequenceImpedance_bch.__class__.__name__} instead)')
        if not isinstance(self.PerLengthSequenceImpedance_g0ch, ConductancePerLength) and self.PerLengthSequenceImpedance_g0ch != None:
            raise ValueError(f'Incorrect datatype in PerLengthSequenceImpedance_g0ch [PerLengthSequenceImpedance] (expected ConductancePerLength but encountered {self.PerLengthSequenceImpedance_g0ch.__class__.__name__} instead)')
        if not isinstance(self.PerLengthSequenceImpedance_gch, ConductancePerLength) and self.PerLengthSequenceImpedance_gch != None:
            raise ValueError(f'Incorrect datatype in PerLengthSequenceImpedance_gch [PerLengthSequenceImpedance] (expected ConductancePerLength but encountered {self.PerLengthSequenceImpedance_gch.__class__.__name__} instead)')
        if not isinstance(self.PerLengthSequenceImpedance_r, ResistancePerLength) and self.PerLengthSequenceImpedance_r != None:
            raise ValueError(f'Incorrect datatype in PerLengthSequenceImpedance_r [PerLengthSequenceImpedance] (expected ResistancePerLength but encountered {self.PerLengthSequenceImpedance_r.__class__.__name__} instead)')
        if not isinstance(self.PerLengthSequenceImpedance_r0, ResistancePerLength) and self.PerLengthSequenceImpedance_r0 != None:
            raise ValueError(f'Incorrect datatype in PerLengthSequenceImpedance_r0 [PerLengthSequenceImpedance] (expected ResistancePerLength but encountered {self.PerLengthSequenceImpedance_r0.__class__.__name__} instead)')
        if not isinstance(self.PerLengthSequenceImpedance_x, ReactancePerLength) and self.PerLengthSequenceImpedance_x != None:
            raise ValueError(f'Incorrect datatype in PerLengthSequenceImpedance_x [PerLengthSequenceImpedance] (expected ReactancePerLength but encountered {self.PerLengthSequenceImpedance_x.__class__.__name__} instead)')
        if not isinstance(self.PerLengthSequenceImpedance_x0, ReactancePerLength) and self.PerLengthSequenceImpedance_x0 != None:
            raise ValueError(f'Incorrect datatype in PerLengthSequenceImpedance_x0 [PerLengthSequenceImpedance] (expected ReactancePerLength but encountered {self.PerLengthSequenceImpedance_x0.__class__.__name__} instead)')
 
class PowerSystemResource(IdentifiedObject):
    """A power system resource can be an item of equipment such as a switch, an equipment container containing many individual items of equipment such as a substation, or an organisational entity such as sub-control area. Power system resources can have measurements associated."""
    def __init__(self, IdentifiedObject_mRID: str = None, IdentifiedObject_name: str = None):
        super().__init__(IdentifiedObject_mRID = IdentifiedObject_mRID, IdentifiedObject_name = IdentifiedObject_name, )
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
    def __init__(self, PowerTransformerEnd_PowerTransformer: 'PowerTransformer' = None, PowerTransformerEnd_connectionKind: 'WindingConnection' = None, PowerTransformerEnd_endNumber: int = None, PowerTransformerEnd_r: 'Resistance' = None, PowerTransformerEnd_r0: 'Resistance' = None, PowerTransformerEnd_ratedS: 'ApparentPower' = None, PowerTransformerEnd_ratedU: 'Voltage' = None, PowerTransformerEnd_x: 'Reactance' = None, PowerTransformerEnd_x0: 'Reactance' = None):
        self.URI = '#' + str(uuid())
        # The power transformer of this power transformer end. 
        self.PowerTransformerEnd_PowerTransformer = PowerTransformerEnd_PowerTransformer
        # Kind of connection. 
        self.PowerTransformerEnd_connectionKind = PowerTransformerEnd_connectionKind
        # Number for this transformer end, corresponding to the end's order in the power transformer vector group or phase angle clock number.  Highest voltage winding should be 1.  Each end within a power transformer should have a unique subsequent end number.   Note the transformer end number need not match the terminal sequence number. 
        self.PowerTransformerEnd_endNumber = PowerTransformerEnd_endNumber
        # Resistance (star-model) of the transformer end. The attribute shall be equal or greater than zero for non-equivalent transformers. 
        self.PowerTransformerEnd_r = PowerTransformerEnd_r
        # Zero sequence series resistance (star-model) of the transformer end. 
        self.PowerTransformerEnd_r0 = PowerTransformerEnd_r0
        # Normal apparent power rating. The attribute shall be a positive value. For a two-winding transformer the values for the high and low voltage sides shall be identical. 
        self.PowerTransformerEnd_ratedS = PowerTransformerEnd_ratedS
        # Rated voltage: phase-phase for three-phase windings, and either phase-phase or phase-neutral for single-phase windings. A high voltage side, as given by TransformerEnd.endNumber, shall have a ratedU that is greater or equal than ratedU for the lower voltage sides. 
        self.PowerTransformerEnd_ratedU = PowerTransformerEnd_ratedU
        # Positive sequence series reactance (star-model) of the transformer end. 
        self.PowerTransformerEnd_x = PowerTransformerEnd_x
        # Zero sequence series reactance of the transformer end. 
        self.PowerTransformerEnd_x0 = PowerTransformerEnd_x0
    @property
    def PowerTransformerEnd_PowerTransformer(self) -> 'PowerTransformer':
        return self.__PowerTransformerEnd_PowerTransformer
    @PowerTransformerEnd_PowerTransformer.setter
    def PowerTransformerEnd_PowerTransformer(self, value: 'PowerTransformer'):
        if value == None:
            self.__PowerTransformerEnd_PowerTransformer = None
        elif not hasattr(self, 'PowerTransformerEnd_PowerTransformer') or not self.PowerTransformerEnd_PowerTransformer is value:
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
        if value == None:
            self.__PowerTransformerEnd_connectionKind = None
        elif not hasattr(self, 'PowerTransformerEnd_connectionKind') or not self.PowerTransformerEnd_connectionKind is value:
            self.__PowerTransformerEnd_connectionKind = WindingConnection(value)
    @property
    def PowerTransformerEnd_endNumber(self) -> int:
        return self.__PowerTransformerEnd_endNumber
    @PowerTransformerEnd_endNumber.setter
    def PowerTransformerEnd_endNumber(self, value: int):
        if value == None:
            self.__PowerTransformerEnd_endNumber = None
        elif not hasattr(self, 'PowerTransformerEnd_endNumber') or not self.PowerTransformerEnd_endNumber is value:
            self.__PowerTransformerEnd_endNumber = int(value)
    @property
    def PowerTransformerEnd_r(self) -> 'Resistance':
        return self.__PowerTransformerEnd_r
    @PowerTransformerEnd_r.setter
    def PowerTransformerEnd_r(self, value: 'Resistance'):
        if value == None:
            self.__PowerTransformerEnd_r = None
        elif not hasattr(self, 'PowerTransformerEnd_r') or not self.PowerTransformerEnd_r is value:
            self.__PowerTransformerEnd_r = value
    @property
    def PowerTransformerEnd_r0(self) -> 'Resistance':
        return self.__PowerTransformerEnd_r0
    @PowerTransformerEnd_r0.setter
    def PowerTransformerEnd_r0(self, value: 'Resistance'):
        if value == None:
            self.__PowerTransformerEnd_r0 = None
        elif not hasattr(self, 'PowerTransformerEnd_r0') or not self.PowerTransformerEnd_r0 is value:
            self.__PowerTransformerEnd_r0 = value
    @property
    def PowerTransformerEnd_ratedS(self) -> 'ApparentPower':
        return self.__PowerTransformerEnd_ratedS
    @PowerTransformerEnd_ratedS.setter
    def PowerTransformerEnd_ratedS(self, value: 'ApparentPower'):
        if value == None:
            self.__PowerTransformerEnd_ratedS = None
        elif not hasattr(self, 'PowerTransformerEnd_ratedS') or not self.PowerTransformerEnd_ratedS is value:
            self.__PowerTransformerEnd_ratedS = value
    @property
    def PowerTransformerEnd_ratedU(self) -> 'Voltage':
        return self.__PowerTransformerEnd_ratedU
    @PowerTransformerEnd_ratedU.setter
    def PowerTransformerEnd_ratedU(self, value: 'Voltage'):
        if value == None:
            self.__PowerTransformerEnd_ratedU = None
        elif not hasattr(self, 'PowerTransformerEnd_ratedU') or not self.PowerTransformerEnd_ratedU is value:
            self.__PowerTransformerEnd_ratedU = value
    @property
    def PowerTransformerEnd_x(self) -> 'Reactance':
        return self.__PowerTransformerEnd_x
    @PowerTransformerEnd_x.setter
    def PowerTransformerEnd_x(self, value: 'Reactance'):
        if value == None:
            self.__PowerTransformerEnd_x = None
        elif not hasattr(self, 'PowerTransformerEnd_x') or not self.PowerTransformerEnd_x is value:
            self.__PowerTransformerEnd_x = value
    @property
    def PowerTransformerEnd_x0(self) -> 'Reactance':
        return self.__PowerTransformerEnd_x0
    @PowerTransformerEnd_x0.setter
    def PowerTransformerEnd_x0(self, value: 'Reactance'):
        if value == None:
            self.__PowerTransformerEnd_x0 = None
        elif not hasattr(self, 'PowerTransformerEnd_x0') or not self.PowerTransformerEnd_x0 is value:
            self.__PowerTransformerEnd_x0 = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.PowerTransformerEnd_PowerTransformer != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.PowerTransformer', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PowerTransformerEnd_PowerTransformer.URI})
        if self.PowerTransformerEnd_connectionKind != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.connectionKind')
            prop.text = self.PowerTransformerEnd_connectionKind.value
        if self.PowerTransformerEnd_endNumber != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.endNumber')
            prop.text = str(self.PowerTransformerEnd_endNumber)
        if self.PowerTransformerEnd_r != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.r', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PowerTransformerEnd_r.URI})
        if self.PowerTransformerEnd_r0 != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.r0', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PowerTransformerEnd_r0.URI})
        if self.PowerTransformerEnd_ratedS != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.ratedS', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PowerTransformerEnd_ratedS.URI})
        if self.PowerTransformerEnd_ratedU != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.ratedU', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PowerTransformerEnd_ratedU.URI})
        if self.PowerTransformerEnd_x != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.x', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PowerTransformerEnd_x.URI})
        if self.PowerTransformerEnd_x0 != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformerEnd.x0', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__PowerTransformerEnd_x0.URI})
        return root
    def validate(self):
        if not isinstance(self.PowerTransformerEnd_PowerTransformer, PowerTransformer):
            raise ValueError(f'Incorrect datatype in PowerTransformerEnd_PowerTransformer [PowerTransformerEnd] (expected PowerTransformer but encountered {self.PowerTransformerEnd_PowerTransformer.__class__.__name__} instead)')
        if not isinstance(self.PowerTransformerEnd_connectionKind, WindingConnection) and self.PowerTransformerEnd_connectionKind != None:
            raise ValueError(f'Incorrect datatype in PowerTransformerEnd_connectionKind [PowerTransformerEnd] (expected WindingConnection but encountered {self.PowerTransformerEnd_connectionKind.__class__.__name__} instead)')
        if not isinstance(self.PowerTransformerEnd_endNumber, int):
            raise ValueError(f'Incorrect datatype in PowerTransformerEnd_endNumber [PowerTransformerEnd] (expected int but encountered {self.PowerTransformerEnd_endNumber.__class__.__name__} instead)')
        if not isinstance(self.PowerTransformerEnd_r, Resistance) and self.PowerTransformerEnd_r != None:
            raise ValueError(f'Incorrect datatype in PowerTransformerEnd_r [PowerTransformerEnd] (expected Resistance but encountered {self.PowerTransformerEnd_r.__class__.__name__} instead)')
        if not isinstance(self.PowerTransformerEnd_r0, Resistance) and self.PowerTransformerEnd_r0 != None:
            raise ValueError(f'Incorrect datatype in PowerTransformerEnd_r0 [PowerTransformerEnd] (expected Resistance but encountered {self.PowerTransformerEnd_r0.__class__.__name__} instead)')
        if not isinstance(self.PowerTransformerEnd_ratedS, ApparentPower):
            raise ValueError(f'Incorrect datatype in PowerTransformerEnd_ratedS [PowerTransformerEnd] (expected ApparentPower but encountered {self.PowerTransformerEnd_ratedS.__class__.__name__} instead)')
        if not isinstance(self.PowerTransformerEnd_ratedU, Voltage):
            raise ValueError(f'Incorrect datatype in PowerTransformerEnd_ratedU [PowerTransformerEnd] (expected Voltage but encountered {self.PowerTransformerEnd_ratedU.__class__.__name__} instead)')
        if not isinstance(self.PowerTransformerEnd_x, Reactance) and self.PowerTransformerEnd_x != None:
            raise ValueError(f'Incorrect datatype in PowerTransformerEnd_x [PowerTransformerEnd] (expected Reactance but encountered {self.PowerTransformerEnd_x.__class__.__name__} instead)')
        if not isinstance(self.PowerTransformerEnd_x0, Reactance) and self.PowerTransformerEnd_x0 != None:
            raise ValueError(f'Incorrect datatype in PowerTransformerEnd_x0 [PowerTransformerEnd] (expected Reactance but encountered {self.PowerTransformerEnd_x0.__class__.__name__} instead)')
 
class Reactance():
    """Reactance (imaginary part of impedance), at rated frequency."""
    def __init__(self, Reactance_multiplier: 'UnitMultiplier' = None, Reactance_unit: 'UnitSymbol' = None, Reactance_value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.Reactance_multiplier = Reactance_multiplier
        self.Reactance_unit = Reactance_unit
        self.Reactance_value = Reactance_value
    @property
    def Reactance_multiplier(self) -> 'UnitMultiplier':
        return self.__Reactance_multiplier
    @Reactance_multiplier.setter
    def Reactance_multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__Reactance_multiplier = None
        elif not hasattr(self, 'Reactance_multiplier') or not self.Reactance_multiplier is value:
            self.__Reactance_multiplier = UnitMultiplier(value)
    @property
    def Reactance_unit(self) -> 'UnitSymbol':
        return self.__Reactance_unit
    @Reactance_unit.setter
    def Reactance_unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__Reactance_unit = None
        elif not hasattr(self, 'Reactance_unit') or not self.Reactance_unit is value:
            self.__Reactance_unit = UnitSymbol(value)
    @property
    def Reactance_value(self) -> Decimal:
        return self.__Reactance_value
    @Reactance_value.setter
    def Reactance_value(self, value: Decimal):
        if value == None:
            self.__Reactance_value = None
        elif not hasattr(self, 'Reactance_value') or not self.Reactance_value is value:
            self.__Reactance_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Reactance', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.Reactance_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Reactance.multiplier')
            prop.text = self.Reactance_multiplier.value
        if self.Reactance_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Reactance.unit')
            prop.text = self.Reactance_unit.value
        if self.Reactance_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Reactance.value')
            prop.text = str(self.Reactance_value)
        return root
    def validate(self):
        if not isinstance(self.Reactance_multiplier, UnitMultiplier):
            raise ValueError(f'Incorrect datatype in Reactance_multiplier [Reactance] (expected UnitMultiplier but encountered {self.Reactance_multiplier.__class__.__name__} instead)')
        if not isinstance(self.Reactance_unit, UnitSymbol):
            raise ValueError(f'Incorrect datatype in Reactance_unit [Reactance] (expected UnitSymbol but encountered {self.Reactance_unit.__class__.__name__} instead)')
        if not isinstance(self.Reactance_value, Decimal):
            raise ValueError(f'Incorrect datatype in Reactance_value [Reactance] (expected Decimal but encountered {self.Reactance_value.__class__.__name__} instead)')
 
class ReactancePerLength():
    """Reactance (imaginary part of impedance) per unit of length, at rated frequency."""
    def __init__(self, ReactancePerLength_multiplier: 'UnitMultiplier' = None, ReactancePerLength_unit: 'UnitSymbol' = None, ReactancePerLength_value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.ReactancePerLength_multiplier = ReactancePerLength_multiplier
        self.ReactancePerLength_unit = ReactancePerLength_unit
        self.ReactancePerLength_value = ReactancePerLength_value
    @property
    def ReactancePerLength_multiplier(self) -> 'UnitMultiplier':
        return self.__ReactancePerLength_multiplier
    @ReactancePerLength_multiplier.setter
    def ReactancePerLength_multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__ReactancePerLength_multiplier = None
        elif not hasattr(self, 'ReactancePerLength_multiplier') or not self.ReactancePerLength_multiplier is value:
            self.__ReactancePerLength_multiplier = UnitMultiplier(value)
    @property
    def ReactancePerLength_unit(self) -> 'UnitSymbol':
        return self.__ReactancePerLength_unit
    @ReactancePerLength_unit.setter
    def ReactancePerLength_unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__ReactancePerLength_unit = None
        elif not hasattr(self, 'ReactancePerLength_unit') or not self.ReactancePerLength_unit is value:
            self.__ReactancePerLength_unit = UnitSymbol(value)
    @property
    def ReactancePerLength_value(self) -> Decimal:
        return self.__ReactancePerLength_value
    @ReactancePerLength_value.setter
    def ReactancePerLength_value(self, value: Decimal):
        if value == None:
            self.__ReactancePerLength_value = None
        elif not hasattr(self, 'ReactancePerLength_value') or not self.ReactancePerLength_value is value:
            self.__ReactancePerLength_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}ReactancePerLength', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.ReactancePerLength_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ReactancePerLength.multiplier')
            prop.text = self.ReactancePerLength_multiplier.value
        if self.ReactancePerLength_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ReactancePerLength.unit')
            prop.text = self.ReactancePerLength_unit.value
        if self.ReactancePerLength_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ReactancePerLength.value')
            prop.text = str(self.ReactancePerLength_value)
        return root
    def validate(self):
        if not isinstance(self.ReactancePerLength_multiplier, UnitMultiplier) and self.ReactancePerLength_multiplier != None:
            raise ValueError(f'Incorrect datatype in ReactancePerLength_multiplier [ReactancePerLength] (expected UnitMultiplier but encountered {self.ReactancePerLength_multiplier.__class__.__name__} instead)')
        if not isinstance(self.ReactancePerLength_unit, UnitSymbol) and self.ReactancePerLength_unit != None:
            raise ValueError(f'Incorrect datatype in ReactancePerLength_unit [ReactancePerLength] (expected UnitSymbol but encountered {self.ReactancePerLength_unit.__class__.__name__} instead)')
        if not isinstance(self.ReactancePerLength_value, Decimal) and self.ReactancePerLength_value != None:
            raise ValueError(f'Incorrect datatype in ReactancePerLength_value [ReactancePerLength] (expected Decimal but encountered {self.ReactancePerLength_value.__class__.__name__} instead)')
 
class ReactivePower():
    """Product of RMS value of the voltage and the RMS value of the quadrature component of the current."""
    def __init__(self, ReactivePower_multiplier: 'UnitMultiplier' = None, ReactivePower_unit: 'UnitSymbol' = None, ReactivePower_value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.ReactivePower_multiplier = ReactivePower_multiplier
        self.ReactivePower_unit = ReactivePower_unit
        self.ReactivePower_value = ReactivePower_value
    @property
    def ReactivePower_multiplier(self) -> 'UnitMultiplier':
        return self.__ReactivePower_multiplier
    @ReactivePower_multiplier.setter
    def ReactivePower_multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__ReactivePower_multiplier = None
        elif not hasattr(self, 'ReactivePower_multiplier') or not self.ReactivePower_multiplier is value:
            self.__ReactivePower_multiplier = UnitMultiplier(value)
    @property
    def ReactivePower_unit(self) -> 'UnitSymbol':
        return self.__ReactivePower_unit
    @ReactivePower_unit.setter
    def ReactivePower_unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__ReactivePower_unit = None
        elif not hasattr(self, 'ReactivePower_unit') or not self.ReactivePower_unit is value:
            self.__ReactivePower_unit = UnitSymbol(value)
    @property
    def ReactivePower_value(self) -> Decimal:
        return self.__ReactivePower_value
    @ReactivePower_value.setter
    def ReactivePower_value(self, value: Decimal):
        if value == None:
            self.__ReactivePower_value = None
        elif not hasattr(self, 'ReactivePower_value') or not self.ReactivePower_value is value:
            self.__ReactivePower_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}ReactivePower', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.ReactivePower_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ReactivePower.multiplier')
            prop.text = self.ReactivePower_multiplier.value
        if self.ReactivePower_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ReactivePower.unit')
            prop.text = self.ReactivePower_unit.value
        if self.ReactivePower_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ReactivePower.value')
            prop.text = str(self.ReactivePower_value)
        return root
    def validate(self):
        if not isinstance(self.ReactivePower_multiplier, UnitMultiplier):
            raise ValueError(f'Incorrect datatype in ReactivePower_multiplier [ReactivePower] (expected UnitMultiplier but encountered {self.ReactivePower_multiplier.__class__.__name__} instead)')
        if not isinstance(self.ReactivePower_unit, UnitSymbol):
            raise ValueError(f'Incorrect datatype in ReactivePower_unit [ReactivePower] (expected UnitSymbol but encountered {self.ReactivePower_unit.__class__.__name__} instead)')
        if not isinstance(self.ReactivePower_value, Decimal):
            raise ValueError(f'Incorrect datatype in ReactivePower_value [ReactivePower] (expected Decimal but encountered {self.ReactivePower_value.__class__.__name__} instead)')
 
class Resistance():
    """Resistance (real part of impedance)."""
    def __init__(self, Resistance_multiplier: 'UnitMultiplier' = None, Resistance_unit: 'UnitSymbol' = None, Resistance_value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.Resistance_multiplier = Resistance_multiplier
        self.Resistance_unit = Resistance_unit
        self.Resistance_value = Resistance_value
    @property
    def Resistance_multiplier(self) -> 'UnitMultiplier':
        return self.__Resistance_multiplier
    @Resistance_multiplier.setter
    def Resistance_multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__Resistance_multiplier = None
        elif not hasattr(self, 'Resistance_multiplier') or not self.Resistance_multiplier is value:
            self.__Resistance_multiplier = UnitMultiplier(value)
    @property
    def Resistance_unit(self) -> 'UnitSymbol':
        return self.__Resistance_unit
    @Resistance_unit.setter
    def Resistance_unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__Resistance_unit = None
        elif not hasattr(self, 'Resistance_unit') or not self.Resistance_unit is value:
            self.__Resistance_unit = UnitSymbol(value)
    @property
    def Resistance_value(self) -> Decimal:
        return self.__Resistance_value
    @Resistance_value.setter
    def Resistance_value(self, value: Decimal):
        if value == None:
            self.__Resistance_value = None
        elif not hasattr(self, 'Resistance_value') or not self.Resistance_value is value:
            self.__Resistance_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Resistance', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.Resistance_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Resistance.multiplier')
            prop.text = self.Resistance_multiplier.value
        if self.Resistance_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Resistance.unit')
            prop.text = self.Resistance_unit.value
        if self.Resistance_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Resistance.value')
            prop.text = str(self.Resistance_value)
        return root
    def validate(self):
        if not isinstance(self.Resistance_multiplier, UnitMultiplier):
            raise ValueError(f'Incorrect datatype in Resistance_multiplier [Resistance] (expected UnitMultiplier but encountered {self.Resistance_multiplier.__class__.__name__} instead)')
        if not isinstance(self.Resistance_unit, UnitSymbol):
            raise ValueError(f'Incorrect datatype in Resistance_unit [Resistance] (expected UnitSymbol but encountered {self.Resistance_unit.__class__.__name__} instead)')
        if not isinstance(self.Resistance_value, Decimal):
            raise ValueError(f'Incorrect datatype in Resistance_value [Resistance] (expected Decimal but encountered {self.Resistance_value.__class__.__name__} instead)')
 
class ResistancePerLength():
    """Resistance (real part of impedance) per unit of length."""
    def __init__(self, ResistancePerLength_multiplier: 'UnitMultiplier' = None, ResistancePerLength_unit: 'UnitSymbol' = None, ResistancePerLength_value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.ResistancePerLength_multiplier = ResistancePerLength_multiplier
        self.ResistancePerLength_unit = ResistancePerLength_unit
        self.ResistancePerLength_value = ResistancePerLength_value
    @property
    def ResistancePerLength_multiplier(self) -> 'UnitMultiplier':
        return self.__ResistancePerLength_multiplier
    @ResistancePerLength_multiplier.setter
    def ResistancePerLength_multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__ResistancePerLength_multiplier = None
        elif not hasattr(self, 'ResistancePerLength_multiplier') or not self.ResistancePerLength_multiplier is value:
            self.__ResistancePerLength_multiplier = UnitMultiplier(value)
    @property
    def ResistancePerLength_unit(self) -> 'UnitSymbol':
        return self.__ResistancePerLength_unit
    @ResistancePerLength_unit.setter
    def ResistancePerLength_unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__ResistancePerLength_unit = None
        elif not hasattr(self, 'ResistancePerLength_unit') or not self.ResistancePerLength_unit is value:
            self.__ResistancePerLength_unit = UnitSymbol(value)
    @property
    def ResistancePerLength_value(self) -> Decimal:
        return self.__ResistancePerLength_value
    @ResistancePerLength_value.setter
    def ResistancePerLength_value(self, value: Decimal):
        if value == None:
            self.__ResistancePerLength_value = None
        elif not hasattr(self, 'ResistancePerLength_value') or not self.ResistancePerLength_value is value:
            self.__ResistancePerLength_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}ResistancePerLength', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.ResistancePerLength_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ResistancePerLength.multiplier')
            prop.text = self.ResistancePerLength_multiplier.value
        if self.ResistancePerLength_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ResistancePerLength.unit')
            prop.text = self.ResistancePerLength_unit.value
        if self.ResistancePerLength_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ResistancePerLength.value')
            prop.text = str(self.ResistancePerLength_value)
        return root
    def validate(self):
        if not isinstance(self.ResistancePerLength_multiplier, UnitMultiplier) and self.ResistancePerLength_multiplier != None:
            raise ValueError(f'Incorrect datatype in ResistancePerLength_multiplier [ResistancePerLength] (expected UnitMultiplier but encountered {self.ResistancePerLength_multiplier.__class__.__name__} instead)')
        if not isinstance(self.ResistancePerLength_unit, UnitSymbol) and self.ResistancePerLength_unit != None:
            raise ValueError(f'Incorrect datatype in ResistancePerLength_unit [ResistancePerLength] (expected UnitSymbol but encountered {self.ResistancePerLength_unit.__class__.__name__} instead)')
        if not isinstance(self.ResistancePerLength_value, Decimal):
            raise ValueError(f'Incorrect datatype in ResistancePerLength_value [ResistancePerLength] (expected Decimal but encountered {self.ResistancePerLength_value.__class__.__name__} instead)')
 
class Susceptance():
    """Imaginary part of admittance."""
    def __init__(self, Susceptance_multiplier: 'UnitMultiplier' = None, Susceptance_unit: 'UnitSymbol' = None, Susceptance_value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.Susceptance_multiplier = Susceptance_multiplier
        self.Susceptance_unit = Susceptance_unit
        self.Susceptance_value = Susceptance_value
    @property
    def Susceptance_multiplier(self) -> 'UnitMultiplier':
        return self.__Susceptance_multiplier
    @Susceptance_multiplier.setter
    def Susceptance_multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__Susceptance_multiplier = None
        elif not hasattr(self, 'Susceptance_multiplier') or not self.Susceptance_multiplier is value:
            self.__Susceptance_multiplier = UnitMultiplier(value)
    @property
    def Susceptance_unit(self) -> 'UnitSymbol':
        return self.__Susceptance_unit
    @Susceptance_unit.setter
    def Susceptance_unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__Susceptance_unit = None
        elif not hasattr(self, 'Susceptance_unit') or not self.Susceptance_unit is value:
            self.__Susceptance_unit = UnitSymbol(value)
    @property
    def Susceptance_value(self) -> Decimal:
        return self.__Susceptance_value
    @Susceptance_value.setter
    def Susceptance_value(self, value: Decimal):
        if value == None:
            self.__Susceptance_value = None
        elif not hasattr(self, 'Susceptance_value') or not self.Susceptance_value is value:
            self.__Susceptance_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Susceptance', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.Susceptance_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Susceptance.multiplier')
            prop.text = self.Susceptance_multiplier.value
        if self.Susceptance_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Susceptance.unit')
            prop.text = self.Susceptance_unit.value
        if self.Susceptance_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Susceptance.value')
            prop.text = str(self.Susceptance_value)
        return root
    def validate(self):
        if not isinstance(self.Susceptance_multiplier, UnitMultiplier):
            raise ValueError(f'Incorrect datatype in Susceptance_multiplier [Susceptance] (expected UnitMultiplier but encountered {self.Susceptance_multiplier.__class__.__name__} instead)')
        if not isinstance(self.Susceptance_unit, UnitSymbol):
            raise ValueError(f'Incorrect datatype in Susceptance_unit [Susceptance] (expected UnitSymbol but encountered {self.Susceptance_unit.__class__.__name__} instead)')
        if not isinstance(self.Susceptance_value, Decimal):
            raise ValueError(f'Incorrect datatype in Susceptance_value [Susceptance] (expected Decimal but encountered {self.Susceptance_value.__class__.__name__} instead)')
 
class SusceptancePerLength():
    """Imaginary part of admittance per unit of length."""
    def __init__(self, SusceptancePerLength_multiplier: 'UnitMultiplier' = None, SusceptancePerLength_unit: 'UnitSymbol' = None, SusceptancePerLength_value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.SusceptancePerLength_multiplier = SusceptancePerLength_multiplier
        self.SusceptancePerLength_unit = SusceptancePerLength_unit
        self.SusceptancePerLength_value = SusceptancePerLength_value
    @property
    def SusceptancePerLength_multiplier(self) -> 'UnitMultiplier':
        return self.__SusceptancePerLength_multiplier
    @SusceptancePerLength_multiplier.setter
    def SusceptancePerLength_multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__SusceptancePerLength_multiplier = None
        elif not hasattr(self, 'SusceptancePerLength_multiplier') or not self.SusceptancePerLength_multiplier is value:
            self.__SusceptancePerLength_multiplier = UnitMultiplier(value)
    @property
    def SusceptancePerLength_unit(self) -> 'UnitSymbol':
        return self.__SusceptancePerLength_unit
    @SusceptancePerLength_unit.setter
    def SusceptancePerLength_unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__SusceptancePerLength_unit = None
        elif not hasattr(self, 'SusceptancePerLength_unit') or not self.SusceptancePerLength_unit is value:
            self.__SusceptancePerLength_unit = UnitSymbol(value)
    @property
    def SusceptancePerLength_value(self) -> Decimal:
        return self.__SusceptancePerLength_value
    @SusceptancePerLength_value.setter
    def SusceptancePerLength_value(self, value: Decimal):
        if value == None:
            self.__SusceptancePerLength_value = None
        elif not hasattr(self, 'SusceptancePerLength_value') or not self.SusceptancePerLength_value is value:
            self.__SusceptancePerLength_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}SusceptancePerLength', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.SusceptancePerLength_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}SusceptancePerLength.multiplier')
            prop.text = self.SusceptancePerLength_multiplier.value
        if self.SusceptancePerLength_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}SusceptancePerLength.unit')
            prop.text = self.SusceptancePerLength_unit.value
        if self.SusceptancePerLength_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}SusceptancePerLength.value')
            prop.text = str(self.SusceptancePerLength_value)
        return root
    def validate(self):
        if not isinstance(self.SusceptancePerLength_multiplier, UnitMultiplier) and self.SusceptancePerLength_multiplier != None:
            raise ValueError(f'Incorrect datatype in SusceptancePerLength_multiplier [SusceptancePerLength] (expected UnitMultiplier but encountered {self.SusceptancePerLength_multiplier.__class__.__name__} instead)')
        if not isinstance(self.SusceptancePerLength_unit, UnitSymbol) and self.SusceptancePerLength_unit != None:
            raise ValueError(f'Incorrect datatype in SusceptancePerLength_unit [SusceptancePerLength] (expected UnitSymbol but encountered {self.SusceptancePerLength_unit.__class__.__name__} instead)')
        if not isinstance(self.SusceptancePerLength_value, Decimal):
            raise ValueError(f'Incorrect datatype in SusceptancePerLength_value [SusceptancePerLength] (expected Decimal but encountered {self.SusceptancePerLength_value.__class__.__name__} instead)')
 
class Terminal():
    """An AC electrical connection point to a piece of conducting equipment. Terminals are connected at physical connection points called connectivity nodes."""
    def __init__(self, Terminal_ConductingEquipment: 'ConductingEquipment' = None, Terminal_ConnectivityNode: 'ConnectivityNode' = None, Terminal_sequenceNumber: int = None):
        self.URI = '#' + str(uuid())
        # The conducting equipment of the terminal.  Conducting equipment have  terminals that may be connected to other conducting equipment terminals via connectivity nodes or topological nodes. 
        self.Terminal_ConductingEquipment = Terminal_ConductingEquipment
        # The connectivity node to which this terminal connects with zero impedance. 
        self.Terminal_ConnectivityNode = Terminal_ConnectivityNode
        # The orientation of the terminal connections for a multiple terminal conducting equipment.  The sequence numbering starts with 1 and additional terminals should follow in increasing order.   The first terminal is the "starting point" for a two terminal branch. 
        self.Terminal_sequenceNumber = Terminal_sequenceNumber
    @property
    def Terminal_ConductingEquipment(self) -> 'ConductingEquipment':
        return self.__Terminal_ConductingEquipment
    @Terminal_ConductingEquipment.setter
    def Terminal_ConductingEquipment(self, value: 'ConductingEquipment'):
        if value == None:
            self.__Terminal_ConductingEquipment = None
        elif not hasattr(self, 'Terminal_ConductingEquipment') or not self.Terminal_ConductingEquipment is value:
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
        if value == None:
            self.__Terminal_ConnectivityNode = None
        elif not hasattr(self, 'Terminal_ConnectivityNode') or not self.Terminal_ConnectivityNode is value:
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
        if value == None:
            self.__Terminal_sequenceNumber = None
        elif not hasattr(self, 'Terminal_sequenceNumber') or not self.Terminal_sequenceNumber is value:
            self.__Terminal_sequenceNumber = int(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Terminal', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.Terminal_ConductingEquipment != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Terminal.ConductingEquipment', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__Terminal_ConductingEquipment.URI})
        if self.Terminal_ConnectivityNode != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Terminal.ConnectivityNode', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__Terminal_ConnectivityNode.URI})
        if self.Terminal_sequenceNumber != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Terminal.sequenceNumber')
            prop.text = str(self.Terminal_sequenceNumber)
        return root
    def validate(self):
        if not isinstance(self.Terminal_ConductingEquipment, ConductingEquipment):
            raise ValueError(f'Incorrect datatype in Terminal_ConductingEquipment [Terminal] (expected ConductingEquipment but encountered {self.Terminal_ConductingEquipment.__class__.__name__} instead)')
        if not isinstance(self.Terminal_ConnectivityNode, ConnectivityNode) and self.Terminal_ConnectivityNode != None:
            raise ValueError(f'Incorrect datatype in Terminal_ConnectivityNode [Terminal] (expected ConnectivityNode but encountered {self.Terminal_ConnectivityNode.__class__.__name__} instead)')
        if not isinstance(self.Terminal_sequenceNumber, int) and self.Terminal_sequenceNumber != None:
            raise ValueError(f'Incorrect datatype in Terminal_sequenceNumber [Terminal] (expected int but encountered {self.Terminal_sequenceNumber.__class__.__name__} instead)')
 
class TopologicalNode(IdentifiedObject):
    """For a detailed substation model a topological node is a set of connectivity nodes that, in the current network state, are connected together through any type of closed switches, including  jumpers. Topological nodes change as the current network state changes (i.e., switches, breakers, etc. change state).
For a planning model, switch statuses are not used to form topological nodes. Instead they are manually created or deleted in a model builder tool. Topological nodes maintained this way are also called "busses"."""
    def __init__(self, TopologicalNode_ConnectivityNodeContainer: 'ConnectivityNodeContainer' = None, TopologicalNode_ConnectivityNodes: List['ConnectivityNode'] = None, TopologicalNode_pInjection: 'ActivePower' = None, TopologicalNode_qInjection: 'ReactivePower' = None, IdentifiedObject_mRID: str = None, IdentifiedObject_name: str = None):
        super().__init__(IdentifiedObject_mRID = IdentifiedObject_mRID, IdentifiedObject_name = IdentifiedObject_name, )
        # The connectivity node container to which the toplogical node belongs. 
        self.TopologicalNode_ConnectivityNodeContainer = TopologicalNode_ConnectivityNodeContainer
        # The connectivity nodes combine together to form this topological node.  May depend on the current state of switches in the network. 
        self.TopologicalNode_ConnectivityNodes = TopologicalNode_ConnectivityNodes
        # The active power injected into the bus at this location in addition to injections from equipment.  Positive sign means injection into the TopologicalNode (bus). Starting value for a steady state solution. 
        self.TopologicalNode_pInjection = TopologicalNode_pInjection
        # The reactive power injected into the bus at this location in addition to injections from equipment. Positive sign means injection into the TopologicalNode (bus). Starting value for a steady state solution. 
        self.TopologicalNode_qInjection = TopologicalNode_qInjection
    @property
    def TopologicalNode_ConnectivityNodeContainer(self) -> 'ConnectivityNodeContainer':
        return self.__TopologicalNode_ConnectivityNodeContainer
    @TopologicalNode_ConnectivityNodeContainer.setter
    def TopologicalNode_ConnectivityNodeContainer(self, value: 'ConnectivityNodeContainer'):
        if value == None:
            self.__TopologicalNode_ConnectivityNodeContainer = None
        elif not hasattr(self, 'TopologicalNode_ConnectivityNodeContainer') or not self.TopologicalNode_ConnectivityNodeContainer is value:
            self.__TopologicalNode_ConnectivityNodeContainer = value
            if isinstance(value.ConnectivityNodeContainer_TopologicalNode, list):
                value.add_ConnectivityNodeContainer_TopologicalNode(self)
            else:
                value.ConnectivityNodeContainer_TopologicalNode = self
    def add_TopologicalNode_ConnectivityNodes(self, value: 'ConnectivityNode'):
        if not hasattr(self, 'TopologicalNode_ConnectivityNodes'):
            self.__TopologicalNode_ConnectivityNodes = []
        if value not in self.__TopologicalNode_ConnectivityNodes:
            self.__TopologicalNode_ConnectivityNodes.append(value)
            if isinstance(value.ConnectivityNode_TopologicalNode, list):
                value.add_ConnectivityNode_TopologicalNode(self)
            else:
                value.ConnectivityNode_TopologicalNode = self
    @property
    def TopologicalNode_ConnectivityNodes(self) -> List['ConnectivityNode']:
        return self.__TopologicalNode_ConnectivityNodes
    @TopologicalNode_ConnectivityNodes.setter
    def TopologicalNode_ConnectivityNodes(self, list_objs: List['ConnectivityNode']):
        if list_objs == None:
            self.__TopologicalNode_ConnectivityNodes = []
            return
        for obj in list_objs:
            self.add_TopologicalNode_ConnectivityNodes(obj)
        if len(list_objs):
            if isinstance(list_objs[0].ConnectivityNode_TopologicalNode, list):
                for obj in list_objs:
                    obj.add_ConnectivityNode_TopologicalNode(self)
            else:
                for obj in list_objs:
                    obj.ConnectivityNode_TopologicalNode = self
    @property
    def TopologicalNode_pInjection(self) -> 'ActivePower':
        return self.__TopologicalNode_pInjection
    @TopologicalNode_pInjection.setter
    def TopologicalNode_pInjection(self, value: 'ActivePower'):
        if value == None:
            self.__TopologicalNode_pInjection = None
        elif not hasattr(self, 'TopologicalNode_pInjection') or not self.TopologicalNode_pInjection is value:
            self.__TopologicalNode_pInjection = value
    @property
    def TopologicalNode_qInjection(self) -> 'ReactivePower':
        return self.__TopologicalNode_qInjection
    @TopologicalNode_qInjection.setter
    def TopologicalNode_qInjection(self, value: 'ReactivePower'):
        if value == None:
            self.__TopologicalNode_qInjection = None
        elif not hasattr(self, 'TopologicalNode_qInjection') or not self.TopologicalNode_qInjection is value:
            self.__TopologicalNode_qInjection = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}TopologicalNode' 
        if self.TopologicalNode_ConnectivityNodeContainer != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}TopologicalNode.ConnectivityNodeContainer', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__TopologicalNode_ConnectivityNodeContainer.URI})
        if self.TopologicalNode_ConnectivityNodes != []:
            for item in self.TopologicalNode_ConnectivityNodes:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}TopologicalNode.ConnectivityNodes', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        if self.TopologicalNode_pInjection != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}TopologicalNode.pInjection', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__TopologicalNode_pInjection.URI})
        if self.TopologicalNode_qInjection != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}TopologicalNode.qInjection', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__TopologicalNode_qInjection.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.TopologicalNode_ConnectivityNodeContainer, ConnectivityNodeContainer) and self.TopologicalNode_ConnectivityNodeContainer != None:
            raise ValueError(f'Incorrect datatype in TopologicalNode_ConnectivityNodeContainer [TopologicalNode] (expected ConnectivityNodeContainer but encountered {self.TopologicalNode_ConnectivityNodeContainer.__class__.__name__} instead)')
        minBound, maxBound = 0, float('Inf')
        if len(self.TopologicalNode_ConnectivityNodes) < minBound or len(self.TopologicalNode_ConnectivityNodes) > maxBound:
            raise ValueError('Incorrect multiplicity in TopologicalNode_ConnectivityNodes [TopologicalNode]')
        if any(not isinstance(item, ConnectivityNode) for item in self.TopologicalNode_ConnectivityNodes):
            raise ValueError(f'Incorrect datatype in TopologicalNode_ConnectivityNodes [TopologicalNode] (expected ConnectivityNode but encountered {self.TopologicalNode_ConnectivityNodes.__class__.__name__} instead)')
        if not isinstance(self.TopologicalNode_pInjection, ActivePower) and self.TopologicalNode_pInjection != None:
            raise ValueError(f'Incorrect datatype in TopologicalNode_pInjection [TopologicalNode] (expected ActivePower but encountered {self.TopologicalNode_pInjection.__class__.__name__} instead)')
        if not isinstance(self.TopologicalNode_qInjection, ReactivePower) and self.TopologicalNode_qInjection != None:
            raise ValueError(f'Incorrect datatype in TopologicalNode_qInjection [TopologicalNode] (expected ReactivePower but encountered {self.TopologicalNode_qInjection.__class__.__name__} instead)')
 
class Voltage():
    """Electrical voltage, can be both AC and DC."""
    def __init__(self, Voltage_multiplier: 'UnitMultiplier' = None, Voltage_unit: 'UnitSymbol' = None, Voltage_value: Decimal = None):
        self.URI = '#' + str(uuid())
        self.Voltage_multiplier = Voltage_multiplier
        self.Voltage_unit = Voltage_unit
        self.Voltage_value = Voltage_value
    @property
    def Voltage_multiplier(self) -> 'UnitMultiplier':
        return self.__Voltage_multiplier
    @Voltage_multiplier.setter
    def Voltage_multiplier(self, value: 'UnitMultiplier'):
        if value == None:
            self.__Voltage_multiplier = None
        elif not hasattr(self, 'Voltage_multiplier') or not self.Voltage_multiplier is value:
            self.__Voltage_multiplier = UnitMultiplier(value)
    @property
    def Voltage_unit(self) -> 'UnitSymbol':
        return self.__Voltage_unit
    @Voltage_unit.setter
    def Voltage_unit(self, value: 'UnitSymbol'):
        if value == None:
            self.__Voltage_unit = None
        elif not hasattr(self, 'Voltage_unit') or not self.Voltage_unit is value:
            self.__Voltage_unit = UnitSymbol(value)
    @property
    def Voltage_value(self) -> Decimal:
        return self.__Voltage_value
    @Voltage_value.setter
    def Voltage_value(self, value: Decimal):
        if value == None:
            self.__Voltage_value = None
        elif not hasattr(self, 'Voltage_value') or not self.Voltage_value is value:
            self.__Voltage_value = Decimal(value)
    def serialize(self) -> ET.Element:
        self.validate()
        root = ET.Element('{grei.ufc.br/DistributionNetwork#}Voltage', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about': self.URI})
        if self.Voltage_multiplier != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Voltage.multiplier')
            prop.text = self.Voltage_multiplier.value
        if self.Voltage_unit != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Voltage.unit')
            prop.text = self.Voltage_unit.value
        if self.Voltage_value != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Voltage.value')
            prop.text = str(self.Voltage_value)
        return root
    def validate(self):
        if not isinstance(self.Voltage_multiplier, UnitMultiplier) and self.Voltage_multiplier != None:
            raise ValueError(f'Incorrect datatype in Voltage_multiplier [Voltage] (expected UnitMultiplier but encountered {self.Voltage_multiplier.__class__.__name__} instead)')
        if not isinstance(self.Voltage_unit, UnitSymbol) and self.Voltage_unit != None:
            raise ValueError(f'Incorrect datatype in Voltage_unit [Voltage] (expected UnitSymbol but encountered {self.Voltage_unit.__class__.__name__} instead)')
        if not isinstance(self.Voltage_value, Decimal) and self.Voltage_value != None:
            raise ValueError(f'Incorrect datatype in Voltage_value [Voltage] (expected Decimal but encountered {self.Voltage_value.__class__.__name__} instead)')
 
class ActivePowerLimit(OperationalLimit):
    """Limit on active power flow."""
    def __init__(self, ActivePowerLimit_value: 'ActivePower' = None):
        super().__init__()
        # Value of active power limit. 
        self.ActivePowerLimit_value = ActivePowerLimit_value
    @property
    def ActivePowerLimit_value(self) -> 'ActivePower':
        return self.__ActivePowerLimit_value
    @ActivePowerLimit_value.setter
    def ActivePowerLimit_value(self, value: 'ActivePower'):
        if value == None:
            self.__ActivePowerLimit_value = None
        elif not hasattr(self, 'ActivePowerLimit_value') or not self.ActivePowerLimit_value is value:
            self.__ActivePowerLimit_value = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}ActivePowerLimit' 
        if self.ActivePowerLimit_value != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ActivePowerLimit.value', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__ActivePowerLimit_value.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.ActivePowerLimit_value, ActivePower):
            raise ValueError(f'Incorrect datatype in ActivePowerLimit_value [ActivePowerLimit] (expected ActivePower but encountered {self.ActivePowerLimit_value.__class__.__name__} instead)')
 
class ApparentPowerLimit(OperationalLimit):
    """Apparent power limit."""
    def __init__(self, ApparentPowerLimit_value: 'ApparentPower' = None):
        super().__init__()
        # The apparent power limit. 
        self.ApparentPowerLimit_value = ApparentPowerLimit_value
    @property
    def ApparentPowerLimit_value(self) -> 'ApparentPower':
        return self.__ApparentPowerLimit_value
    @ApparentPowerLimit_value.setter
    def ApparentPowerLimit_value(self, value: 'ApparentPower'):
        if value == None:
            self.__ApparentPowerLimit_value = None
        elif not hasattr(self, 'ApparentPowerLimit_value') or not self.ApparentPowerLimit_value is value:
            self.__ApparentPowerLimit_value = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}ApparentPowerLimit' 
        if self.ApparentPowerLimit_value != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ApparentPowerLimit.value', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__ApparentPowerLimit_value.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.ApparentPowerLimit_value, ApparentPower):
            raise ValueError(f'Incorrect datatype in ApparentPowerLimit_value [ApparentPowerLimit] (expected ApparentPower but encountered {self.ApparentPowerLimit_value.__class__.__name__} instead)')
 
class ConnectivityNode(IdentifiedObject):
    """Connectivity nodes are points where terminals of AC conducting equipment are connected together with zero impedance."""
    def __init__(self, ConnectivityNode_Terminals: List['Terminal'] = None, ConnectivityNode_TopologicalNode: 'TopologicalNode' = None, IdentifiedObject_mRID: str = None, IdentifiedObject_name: str = None):
        super().__init__(IdentifiedObject_mRID = IdentifiedObject_mRID, IdentifiedObject_name = IdentifiedObject_name, )
        # Terminals interconnected with zero impedance at a this connectivity node. 
        self.ConnectivityNode_Terminals = ConnectivityNode_Terminals
        # The topological node to which this connectivity node is assigned.  May depend on the current state of switches in the network. 
        self.ConnectivityNode_TopologicalNode = ConnectivityNode_TopologicalNode
    def add_ConnectivityNode_Terminals(self, value: 'Terminal'):
        if not hasattr(self, 'ConnectivityNode_Terminals'):
            self.__ConnectivityNode_Terminals = []
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
        if list_objs == None:
            self.__ConnectivityNode_Terminals = []
            return
        for obj in list_objs:
            self.add_ConnectivityNode_Terminals(obj)
        if len(list_objs):
            if isinstance(list_objs[0].Terminal_ConnectivityNode, list):
                for obj in list_objs:
                    obj.add_Terminal_ConnectivityNode(self)
            else:
                for obj in list_objs:
                    obj.Terminal_ConnectivityNode = self
    @property
    def ConnectivityNode_TopologicalNode(self) -> 'TopologicalNode':
        return self.__ConnectivityNode_TopologicalNode
    @ConnectivityNode_TopologicalNode.setter
    def ConnectivityNode_TopologicalNode(self, value: 'TopologicalNode'):
        if value == None:
            self.__ConnectivityNode_TopologicalNode = None
        elif not hasattr(self, 'ConnectivityNode_TopologicalNode') or not self.ConnectivityNode_TopologicalNode is value:
            self.__ConnectivityNode_TopologicalNode = value
            if isinstance(value.TopologicalNode_ConnectivityNodes, list):
                value.add_TopologicalNode_ConnectivityNodes(self)
            else:
                value.TopologicalNode_ConnectivityNodes = self
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}ConnectivityNode' 
        if self.ConnectivityNode_Terminals != []:
            for item in self.ConnectivityNode_Terminals:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ConnectivityNode.Terminals', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        if self.ConnectivityNode_TopologicalNode != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ConnectivityNode.TopologicalNode', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__ConnectivityNode_TopologicalNode.URI})
        return root
    def validate(self):
        super().validate()
        minBound, maxBound = 0, float('Inf')
        if len(self.ConnectivityNode_Terminals) < minBound or len(self.ConnectivityNode_Terminals) > maxBound:
            raise ValueError('Incorrect multiplicity in ConnectivityNode_Terminals [ConnectivityNode]')
        if any(not isinstance(item, Terminal) for item in self.ConnectivityNode_Terminals):
            raise ValueError(f'Incorrect datatype in ConnectivityNode_Terminals [ConnectivityNode] (expected Terminal but encountered {self.ConnectivityNode_Terminals.__class__.__name__} instead)')
        if not isinstance(self.ConnectivityNode_TopologicalNode, TopologicalNode) and self.ConnectivityNode_TopologicalNode != None:
            raise ValueError(f'Incorrect datatype in ConnectivityNode_TopologicalNode [ConnectivityNode] (expected TopologicalNode but encountered {self.ConnectivityNode_TopologicalNode.__class__.__name__} instead)')
 
class ConnectivityNodeContainer(PowerSystemResource):
    """A base class for all objects that may contain connectivity nodes or topological nodes."""
    def __init__(self, ConnectivityNodeContainer_TopologicalNode: List['TopologicalNode'] = None, IdentifiedObject_mRID: str = None, IdentifiedObject_name: str = None):
        super().__init__(IdentifiedObject_mRID = IdentifiedObject_mRID, IdentifiedObject_name = IdentifiedObject_name, )
        # The topological nodes which belong to this connectivity node container. 
        self.ConnectivityNodeContainer_TopologicalNode = ConnectivityNodeContainer_TopologicalNode
    def add_ConnectivityNodeContainer_TopologicalNode(self, value: 'TopologicalNode'):
        if not hasattr(self, 'ConnectivityNodeContainer_TopologicalNode'):
            self.__ConnectivityNodeContainer_TopologicalNode = []
        if value not in self.__ConnectivityNodeContainer_TopologicalNode:
            self.__ConnectivityNodeContainer_TopologicalNode.append(value)
            if isinstance(value.TopologicalNode_ConnectivityNodeContainer, list):
                value.add_TopologicalNode_ConnectivityNodeContainer(self)
            else:
                value.TopologicalNode_ConnectivityNodeContainer = self
    @property
    def ConnectivityNodeContainer_TopologicalNode(self) -> List['TopologicalNode']:
        return self.__ConnectivityNodeContainer_TopologicalNode
    @ConnectivityNodeContainer_TopologicalNode.setter
    def ConnectivityNodeContainer_TopologicalNode(self, list_objs: List['TopologicalNode']):
        if list_objs == None:
            self.__ConnectivityNodeContainer_TopologicalNode = []
            return
        for obj in list_objs:
            self.add_ConnectivityNodeContainer_TopologicalNode(obj)
        if len(list_objs):
            if isinstance(list_objs[0].TopologicalNode_ConnectivityNodeContainer, list):
                for obj in list_objs:
                    obj.add_TopologicalNode_ConnectivityNodeContainer(self)
            else:
                for obj in list_objs:
                    obj.TopologicalNode_ConnectivityNodeContainer = self
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}ConnectivityNodeContainer' 
        if self.ConnectivityNodeContainer_TopologicalNode != []:
            for item in self.ConnectivityNodeContainer_TopologicalNode:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ConnectivityNodeContainer.TopologicalNode', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        return root
    def validate(self):
        super().validate()
        minBound, maxBound = 0, float('Inf')
        if len(self.ConnectivityNodeContainer_TopologicalNode) < minBound or len(self.ConnectivityNodeContainer_TopologicalNode) > maxBound:
            raise ValueError('Incorrect multiplicity in ConnectivityNodeContainer_TopologicalNode [ConnectivityNodeContainer]')
        if any(not isinstance(item, TopologicalNode) for item in self.ConnectivityNodeContainer_TopologicalNode):
            raise ValueError(f'Incorrect datatype in ConnectivityNodeContainer_TopologicalNode [ConnectivityNodeContainer] (expected TopologicalNode but encountered {self.ConnectivityNodeContainer_TopologicalNode.__class__.__name__} instead)')
 
class CurrentLimit(OperationalLimit):
    """Operational limit on current."""
    def __init__(self, CurrentLimit_value: 'CurrentFlow' = None):
        super().__init__()
        # Limit on current flow. 
        self.CurrentLimit_value = CurrentLimit_value
    @property
    def CurrentLimit_value(self) -> 'CurrentFlow':
        return self.__CurrentLimit_value
    @CurrentLimit_value.setter
    def CurrentLimit_value(self, value: 'CurrentFlow'):
        if value == None:
            self.__CurrentLimit_value = None
        elif not hasattr(self, 'CurrentLimit_value') or not self.CurrentLimit_value is value:
            self.__CurrentLimit_value = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}CurrentLimit' 
        if self.CurrentLimit_value != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}CurrentLimit.value', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__CurrentLimit_value.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.CurrentLimit_value, CurrentFlow):
            raise ValueError(f'Incorrect datatype in CurrentLimit_value [CurrentLimit] (expected CurrentFlow but encountered {self.CurrentLimit_value.__class__.__name__} instead)')
 
class Equipment(PowerSystemResource):
    """The parts of a power system that are physical devices, electronic or mechanical."""
    def __init__(self, Equipment_EquipmentContainer: 'EquipmentContainer' = None, Equipment_OperationalLimitSet: List['OperationalLimitSet'] = None, IdentifiedObject_mRID: str = None, IdentifiedObject_name: str = None):
        super().__init__(IdentifiedObject_mRID = IdentifiedObject_mRID, IdentifiedObject_name = IdentifiedObject_name, )
        # Container of this equipment. 
        self.Equipment_EquipmentContainer = Equipment_EquipmentContainer
        # The operational limit sets associated with this equipment. 
        self.Equipment_OperationalLimitSet = Equipment_OperationalLimitSet
    @property
    def Equipment_EquipmentContainer(self) -> 'EquipmentContainer':
        return self.__Equipment_EquipmentContainer
    @Equipment_EquipmentContainer.setter
    def Equipment_EquipmentContainer(self, value: 'EquipmentContainer'):
        if value == None:
            self.__Equipment_EquipmentContainer = None
        elif not hasattr(self, 'Equipment_EquipmentContainer') or not self.Equipment_EquipmentContainer is value:
            self.__Equipment_EquipmentContainer = value
            if isinstance(value.EquipmentContainer_Equipments, list):
                value.add_EquipmentContainer_Equipments(self)
            else:
                value.EquipmentContainer_Equipments = self
    def add_Equipment_OperationalLimitSet(self, value: 'OperationalLimitSet'):
        if not hasattr(self, 'Equipment_OperationalLimitSet'):
            self.__Equipment_OperationalLimitSet = []
        if value not in self.__Equipment_OperationalLimitSet:
            self.__Equipment_OperationalLimitSet.append(value)
    @property
    def Equipment_OperationalLimitSet(self) -> List['OperationalLimitSet']:
        return self.__Equipment_OperationalLimitSet
    @Equipment_OperationalLimitSet.setter
    def Equipment_OperationalLimitSet(self, list_objs: List['OperationalLimitSet']):
        if list_objs == None:
            self.__Equipment_OperationalLimitSet = []
            return
        for obj in list_objs:
            self.add_Equipment_OperationalLimitSet(obj)
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}Equipment' 
        if self.Equipment_EquipmentContainer != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Equipment.EquipmentContainer', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__Equipment_EquipmentContainer.URI})
        if self.Equipment_OperationalLimitSet != []:
            for item in self.Equipment_OperationalLimitSet:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Equipment.OperationalLimitSet', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.Equipment_EquipmentContainer, EquipmentContainer) and self.Equipment_EquipmentContainer != None:
            raise ValueError(f'Incorrect datatype in Equipment_EquipmentContainer [Equipment] (expected EquipmentContainer but encountered {self.Equipment_EquipmentContainer.__class__.__name__} instead)')
        minBound, maxBound = 0, float('Inf')
        if len(self.Equipment_OperationalLimitSet) < minBound or len(self.Equipment_OperationalLimitSet) > maxBound:
            raise ValueError('Incorrect multiplicity in Equipment_OperationalLimitSet [Equipment]')
        if any(not isinstance(item, OperationalLimitSet) for item in self.Equipment_OperationalLimitSet):
            raise ValueError(f'Incorrect datatype in Equipment_OperationalLimitSet [Equipment] (expected OperationalLimitSet but encountered {self.Equipment_OperationalLimitSet.__class__.__name__} instead)')
 
class EquipmentContainer(PowerSystemResource):
    """A modeling construct to provide a root class for containing equipment."""
    def __init__(self, EquipmentContainer_Equipments: List['Equipment'] = None, IdentifiedObject_mRID: str = None, IdentifiedObject_name: str = None):
        super().__init__(IdentifiedObject_mRID = IdentifiedObject_mRID, IdentifiedObject_name = IdentifiedObject_name, )
        # Contained equipment. 
        self.EquipmentContainer_Equipments = EquipmentContainer_Equipments
    def add_EquipmentContainer_Equipments(self, value: 'Equipment'):
        if not hasattr(self, 'EquipmentContainer_Equipments'):
            self.__EquipmentContainer_Equipments = []
        if value not in self.__EquipmentContainer_Equipments:
            self.__EquipmentContainer_Equipments.append(value)
            if isinstance(value.Equipment_EquipmentContainer, list):
                value.add_Equipment_EquipmentContainer(self)
            else:
                value.Equipment_EquipmentContainer = self
    @property
    def EquipmentContainer_Equipments(self) -> List['Equipment']:
        return self.__EquipmentContainer_Equipments
    @EquipmentContainer_Equipments.setter
    def EquipmentContainer_Equipments(self, list_objs: List['Equipment']):
        if list_objs == None:
            self.__EquipmentContainer_Equipments = []
            return
        for obj in list_objs:
            self.add_EquipmentContainer_Equipments(obj)
        if len(list_objs):
            if isinstance(list_objs[0].Equipment_EquipmentContainer, list):
                for obj in list_objs:
                    obj.add_Equipment_EquipmentContainer(self)
            else:
                for obj in list_objs:
                    obj.Equipment_EquipmentContainer = self
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}EquipmentContainer' 
        if self.EquipmentContainer_Equipments != []:
            for item in self.EquipmentContainer_Equipments:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EquipmentContainer.Equipments', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        return root
    def validate(self):
        super().validate()
        minBound, maxBound = 0, float('Inf')
        if len(self.EquipmentContainer_Equipments) < minBound or len(self.EquipmentContainer_Equipments) > maxBound:
            raise ValueError('Incorrect multiplicity in EquipmentContainer_Equipments [EquipmentContainer]')
        if any(not isinstance(item, Equipment) for item in self.EquipmentContainer_Equipments):
            raise ValueError(f'Incorrect datatype in EquipmentContainer_Equipments [EquipmentContainer] (expected Equipment but encountered {self.EquipmentContainer_Equipments.__class__.__name__} instead)')
 
class Feeder(ConnectivityNodeContainer):
    """"""
    def __init__(self, Feeder_FeedingSubstation: 'Substation' = None, ConnectivityNodeContainer_TopologicalNode: List['TopologicalNode'] = None, IdentifiedObject_mRID: str = None, IdentifiedObject_name: str = None):
        super().__init__(ConnectivityNodeContainer_TopologicalNode = ConnectivityNodeContainer_TopologicalNode, IdentifiedObject_mRID = IdentifiedObject_mRID, IdentifiedObject_name = IdentifiedObject_name, )
        self.Feeder_FeedingSubstation = Feeder_FeedingSubstation
    @property
    def Feeder_FeedingSubstation(self) -> 'Substation':
        return self.__Feeder_FeedingSubstation
    @Feeder_FeedingSubstation.setter
    def Feeder_FeedingSubstation(self, value: 'Substation'):
        if value == None:
            self.__Feeder_FeedingSubstation = None
        elif not hasattr(self, 'Feeder_FeedingSubstation') or not self.Feeder_FeedingSubstation is value:
            self.__Feeder_FeedingSubstation = value
            if isinstance(value.Substation_SubstationFeeder, list):
                value.add_Substation_SubstationFeeder(self)
            else:
                value.Substation_SubstationFeeder = self
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}Feeder' 
        if self.Feeder_FeedingSubstation != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Feeder.FeedingSubstation', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__Feeder_FeedingSubstation.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.Feeder_FeedingSubstation, Substation) and self.Feeder_FeedingSubstation != None:
            raise ValueError(f'Incorrect datatype in Feeder_FeedingSubstation [Feeder] (expected Substation but encountered {self.Feeder_FeedingSubstation.__class__.__name__} instead)')
 
class Substation(EquipmentContainer):
    """A collection of equipment for purposes other than generation or utilization, through which electric energy in bulk is passed for the purposes of switching or modifying its characteristics."""
    def __init__(self, Substation_SubstationFeeder: List['Feeder'] = None, EquipmentContainer_Equipments: List['Equipment'] = None, IdentifiedObject_mRID: str = None, IdentifiedObject_name: str = None):
        super().__init__(EquipmentContainer_Equipments = EquipmentContainer_Equipments, IdentifiedObject_mRID = IdentifiedObject_mRID, IdentifiedObject_name = IdentifiedObject_name, )
        self.Substation_SubstationFeeder = Substation_SubstationFeeder
    def add_Substation_SubstationFeeder(self, value: 'Feeder'):
        if not hasattr(self, 'Substation_SubstationFeeder'):
            self.__Substation_SubstationFeeder = []
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
        if list_objs == None:
            self.__Substation_SubstationFeeder = []
            return
        for obj in list_objs:
            self.add_Substation_SubstationFeeder(obj)
        if len(list_objs):
            if isinstance(list_objs[0].Feeder_FeedingSubstation, list):
                for obj in list_objs:
                    obj.add_Feeder_FeedingSubstation(self)
            else:
                for obj in list_objs:
                    obj.Feeder_FeedingSubstation = self
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}Substation' 
        if self.Substation_SubstationFeeder != []:
            for item in self.Substation_SubstationFeeder:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Substation.SubstationFeeder', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        return root
    def validate(self):
        super().validate()
        minBound, maxBound = 0, float('Inf')
        if len(self.Substation_SubstationFeeder) < minBound or len(self.Substation_SubstationFeeder) > maxBound:
            raise ValueError('Incorrect multiplicity in Substation_SubstationFeeder [Substation]')
        if any(not isinstance(item, Feeder) for item in self.Substation_SubstationFeeder):
            raise ValueError(f'Incorrect datatype in Substation_SubstationFeeder [Substation] (expected Feeder but encountered {self.Substation_SubstationFeeder.__class__.__name__} instead)')
 
class ConductingEquipment(Equipment):
    """The parts of the AC power system that are designed to carry current or that are conductively connected through terminals."""
    def __init__(self, ConductingEquipment_Terminals: List['Terminal'] = None, Equipment_EquipmentContainer: 'EquipmentContainer' = None, Equipment_OperationalLimitSet: List['OperationalLimitSet'] = None, IdentifiedObject_mRID: str = None, IdentifiedObject_name: str = None):
        super().__init__(Equipment_EquipmentContainer = Equipment_EquipmentContainer, Equipment_OperationalLimitSet = Equipment_OperationalLimitSet, IdentifiedObject_mRID = IdentifiedObject_mRID, IdentifiedObject_name = IdentifiedObject_name, )
        # Conducting equipment have terminals that may be connected to other conducting equipment terminals via connectivity nodes or topological nodes. 
        self.ConductingEquipment_Terminals = ConductingEquipment_Terminals
    def add_ConductingEquipment_Terminals(self, value: 'Terminal'):
        if not hasattr(self, 'ConductingEquipment_Terminals'):
            self.__ConductingEquipment_Terminals = []
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
        if list_objs == None:
            self.__ConductingEquipment_Terminals = []
            return
        for obj in list_objs:
            self.add_ConductingEquipment_Terminals(obj)
        if len(list_objs):
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
        if self.ConductingEquipment_Terminals != []:
            for item in self.ConductingEquipment_Terminals:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ConductingEquipment.Terminals', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        return root
    def validate(self):
        super().validate()
        minBound, maxBound = 0, float('Inf')
        if len(self.ConductingEquipment_Terminals) < minBound or len(self.ConductingEquipment_Terminals) > maxBound:
            raise ValueError('Incorrect multiplicity in ConductingEquipment_Terminals [ConductingEquipment]')
        if any(not isinstance(item, Terminal) for item in self.ConductingEquipment_Terminals):
            raise ValueError(f'Incorrect datatype in ConductingEquipment_Terminals [ConductingEquipment] (expected Terminal but encountered {self.ConductingEquipment_Terminals.__class__.__name__} instead)')
 
class Conductor(ConductingEquipment):
    """Combination of conducting material with consistent electrical characteristics, building a single electrical system, used to carry current between points in the power system."""
    def __init__(self, Conductor_length: 'Length' = None, ConductingEquipment_Terminals: List['Terminal'] = None, Equipment_EquipmentContainer: 'EquipmentContainer' = None, Equipment_OperationalLimitSet: List['OperationalLimitSet'] = None, IdentifiedObject_mRID: str = None, IdentifiedObject_name: str = None):
        super().__init__(ConductingEquipment_Terminals = ConductingEquipment_Terminals, Equipment_EquipmentContainer = Equipment_EquipmentContainer, Equipment_OperationalLimitSet = Equipment_OperationalLimitSet, IdentifiedObject_mRID = IdentifiedObject_mRID, IdentifiedObject_name = IdentifiedObject_name, )
        # Segment length for calculating line section capabilities 
        self.Conductor_length = Conductor_length
    @property
    def Conductor_length(self) -> 'Length':
        return self.__Conductor_length
    @Conductor_length.setter
    def Conductor_length(self, value: 'Length'):
        if value == None:
            self.__Conductor_length = None
        elif not hasattr(self, 'Conductor_length') or not self.Conductor_length is value:
            self.__Conductor_length = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}Conductor' 
        if self.Conductor_length != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Conductor.length', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__Conductor_length.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.Conductor_length, Length):
            raise ValueError(f'Incorrect datatype in Conductor_length [Conductor] (expected Length but encountered {self.Conductor_length.__class__.__name__} instead)')
 
class EnergyConsumer(ConductingEquipment):
    """Generic user of energy - a  point of consumption on the power system model."""
    def __init__(self, EnergyConsumer_p: 'ActivePower' = None, EnergyConsumer_q: 'ReactivePower' = None, ConductingEquipment_Terminals: List['Terminal'] = None, Equipment_EquipmentContainer: 'EquipmentContainer' = None, Equipment_OperationalLimitSet: List['OperationalLimitSet'] = None, IdentifiedObject_mRID: str = None, IdentifiedObject_name: str = None):
        super().__init__(ConductingEquipment_Terminals = ConductingEquipment_Terminals, Equipment_EquipmentContainer = Equipment_EquipmentContainer, Equipment_OperationalLimitSet = Equipment_OperationalLimitSet, IdentifiedObject_mRID = IdentifiedObject_mRID, IdentifiedObject_name = IdentifiedObject_name, )
        # Active power of the load. Load sign convention is used, i.e. positive sign means flow out from a node. For voltage dependent loads the value is at rated voltage. Starting value for a steady state solution. 
        self.EnergyConsumer_p = EnergyConsumer_p
        # Reactive power of the load. Load sign convention is used, i.e. positive sign means flow out from a node. For voltage dependent loads the value is at rated voltage. Starting value for a steady state solution. 
        self.EnergyConsumer_q = EnergyConsumer_q
    @property
    def EnergyConsumer_p(self) -> 'ActivePower':
        return self.__EnergyConsumer_p
    @EnergyConsumer_p.setter
    def EnergyConsumer_p(self, value: 'ActivePower'):
        if value == None:
            self.__EnergyConsumer_p = None
        elif not hasattr(self, 'EnergyConsumer_p') or not self.EnergyConsumer_p is value:
            self.__EnergyConsumer_p = value
    @property
    def EnergyConsumer_q(self) -> 'ReactivePower':
        return self.__EnergyConsumer_q
    @EnergyConsumer_q.setter
    def EnergyConsumer_q(self, value: 'ReactivePower'):
        if value == None:
            self.__EnergyConsumer_q = None
        elif not hasattr(self, 'EnergyConsumer_q') or not self.EnergyConsumer_q is value:
            self.__EnergyConsumer_q = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}EnergyConsumer' 
        if self.EnergyConsumer_p != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EnergyConsumer.p', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__EnergyConsumer_p.URI})
        if self.EnergyConsumer_q != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EnergyConsumer.q', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__EnergyConsumer_q.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.EnergyConsumer_p, ActivePower):
            raise ValueError(f'Incorrect datatype in EnergyConsumer_p [EnergyConsumer] (expected ActivePower but encountered {self.EnergyConsumer_p.__class__.__name__} instead)')
        if not isinstance(self.EnergyConsumer_q, ReactivePower):
            raise ValueError(f'Incorrect datatype in EnergyConsumer_q [EnergyConsumer] (expected ReactivePower but encountered {self.EnergyConsumer_q.__class__.__name__} instead)')
 
class EquivalentInjection(ConductingEquipment):
    """This class represents equivalent injections (generation or load).  Voltage regulation is allowed only at the point of connection."""
    def __init__(self, EquivalentInjection_BaseVoltage: 'BaseVoltage' = None, EquivalentInjection_r: 'Resistance' = None, EquivalentInjection_r0: 'Resistance' = None, EquivalentInjection_x: 'Reactance' = None, EquivalentInjection_x0: 'Reactance' = None, ConductingEquipment_Terminals: List['Terminal'] = None, Equipment_EquipmentContainer: 'EquipmentContainer' = None, Equipment_OperationalLimitSet: List['OperationalLimitSet'] = None, IdentifiedObject_mRID: str = None, IdentifiedObject_name: str = None):
        super().__init__(ConductingEquipment_Terminals = ConductingEquipment_Terminals, Equipment_EquipmentContainer = Equipment_EquipmentContainer, Equipment_OperationalLimitSet = Equipment_OperationalLimitSet, IdentifiedObject_mRID = IdentifiedObject_mRID, IdentifiedObject_name = IdentifiedObject_name, )
        # Base voltage of this conducting equipment.  Use only when there is no voltage level container used and only one base voltage applies.  For example, not used for transformers. 
        self.EquivalentInjection_BaseVoltage = EquivalentInjection_BaseVoltage
        # Positive sequence resistance. Used to represent Extended-Ward (IEC 60909). Usage : Extended-Ward is a result of network reduction prior to the data exchange. 
        self.EquivalentInjection_r = EquivalentInjection_r
        # Zero sequence resistance. Used to represent Extended-Ward (IEC 60909). Usage : Extended-Ward is a result of network reduction prior to the data exchange. 
        self.EquivalentInjection_r0 = EquivalentInjection_r0
        # Positive sequence reactance. Used to represent Extended-Ward (IEC 60909). Usage : Extended-Ward is a result of network reduction prior to the data exchange. 
        self.EquivalentInjection_x = EquivalentInjection_x
        # Zero sequence reactance. Used to represent Extended-Ward (IEC 60909). Usage : Extended-Ward is a result of network reduction prior to the data exchange. 
        self.EquivalentInjection_x0 = EquivalentInjection_x0
    @property
    def EquivalentInjection_BaseVoltage(self) -> 'BaseVoltage':
        return self.__EquivalentInjection_BaseVoltage
    @EquivalentInjection_BaseVoltage.setter
    def EquivalentInjection_BaseVoltage(self, value: 'BaseVoltage'):
        if value == None:
            self.__EquivalentInjection_BaseVoltage = None
        elif not hasattr(self, 'EquivalentInjection_BaseVoltage') or not self.EquivalentInjection_BaseVoltage is value:
            self.__EquivalentInjection_BaseVoltage = value
    @property
    def EquivalentInjection_r(self) -> 'Resistance':
        return self.__EquivalentInjection_r
    @EquivalentInjection_r.setter
    def EquivalentInjection_r(self, value: 'Resistance'):
        if value == None:
            self.__EquivalentInjection_r = None
        elif not hasattr(self, 'EquivalentInjection_r') or not self.EquivalentInjection_r is value:
            self.__EquivalentInjection_r = value
    @property
    def EquivalentInjection_r0(self) -> 'Resistance':
        return self.__EquivalentInjection_r0
    @EquivalentInjection_r0.setter
    def EquivalentInjection_r0(self, value: 'Resistance'):
        if value == None:
            self.__EquivalentInjection_r0 = None
        elif not hasattr(self, 'EquivalentInjection_r0') or not self.EquivalentInjection_r0 is value:
            self.__EquivalentInjection_r0 = value
    @property
    def EquivalentInjection_x(self) -> 'Reactance':
        return self.__EquivalentInjection_x
    @EquivalentInjection_x.setter
    def EquivalentInjection_x(self, value: 'Reactance'):
        if value == None:
            self.__EquivalentInjection_x = None
        elif not hasattr(self, 'EquivalentInjection_x') or not self.EquivalentInjection_x is value:
            self.__EquivalentInjection_x = value
    @property
    def EquivalentInjection_x0(self) -> 'Reactance':
        return self.__EquivalentInjection_x0
    @EquivalentInjection_x0.setter
    def EquivalentInjection_x0(self, value: 'Reactance'):
        if value == None:
            self.__EquivalentInjection_x0 = None
        elif not hasattr(self, 'EquivalentInjection_x0') or not self.EquivalentInjection_x0 is value:
            self.__EquivalentInjection_x0 = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}EquivalentInjection' 
        if self.EquivalentInjection_BaseVoltage != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EquivalentInjection.BaseVoltage', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__EquivalentInjection_BaseVoltage.URI})
        if self.EquivalentInjection_r != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EquivalentInjection.r', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__EquivalentInjection_r.URI})
        if self.EquivalentInjection_r0 != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EquivalentInjection.r0', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__EquivalentInjection_r0.URI})
        if self.EquivalentInjection_x != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EquivalentInjection.x', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__EquivalentInjection_x.URI})
        if self.EquivalentInjection_x0 != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}EquivalentInjection.x0', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__EquivalentInjection_x0.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.EquivalentInjection_BaseVoltage, BaseVoltage):
            raise ValueError(f'Incorrect datatype in EquivalentInjection_BaseVoltage [EquivalentInjection] (expected BaseVoltage but encountered {self.EquivalentInjection_BaseVoltage.__class__.__name__} instead)')
        if not isinstance(self.EquivalentInjection_r, Resistance) and self.EquivalentInjection_r != None:
            raise ValueError(f'Incorrect datatype in EquivalentInjection_r [EquivalentInjection] (expected Resistance but encountered {self.EquivalentInjection_r.__class__.__name__} instead)')
        if not isinstance(self.EquivalentInjection_r0, Resistance) and self.EquivalentInjection_r0 != None:
            raise ValueError(f'Incorrect datatype in EquivalentInjection_r0 [EquivalentInjection] (expected Resistance but encountered {self.EquivalentInjection_r0.__class__.__name__} instead)')
        if not isinstance(self.EquivalentInjection_x, Reactance) and self.EquivalentInjection_x != None:
            raise ValueError(f'Incorrect datatype in EquivalentInjection_x [EquivalentInjection] (expected Reactance but encountered {self.EquivalentInjection_x.__class__.__name__} instead)')
        if not isinstance(self.EquivalentInjection_x0, Reactance) and self.EquivalentInjection_x0 != None:
            raise ValueError(f'Incorrect datatype in EquivalentInjection_x0 [EquivalentInjection] (expected Reactance but encountered {self.EquivalentInjection_x0.__class__.__name__} instead)')
 
class PowerTransformer(ConductingEquipment):
    """An electrical device consisting of  two or more coupled windings, with or without a magnetic core, for introducing mutual coupling between electric circuits. Transformers can be used to control voltage and phase shift (active power flow).
A power transformer may be composed of separate transformer tanks that need not be identical.
A power transformer can be modeled with or without tanks and is intended for use in both balanced and unbalanced representations.   A power transformer typically has two terminals, but may have one (grounding), three or more terminals.
The inherited association ConductingEquipment.BaseVoltage should not be used.  The association from TransformerEnd to BaseVoltage should be used instead."""
    def __init__(self, PowerTransformer_PowerTransformerEnd: List['PowerTransformerEnd'] = None, ConductingEquipment_Terminals: List['Terminal'] = None, Equipment_EquipmentContainer: 'EquipmentContainer' = None, Equipment_OperationalLimitSet: List['OperationalLimitSet'] = None, IdentifiedObject_mRID: str = None, IdentifiedObject_name: str = None):
        super().__init__(ConductingEquipment_Terminals = ConductingEquipment_Terminals, Equipment_EquipmentContainer = Equipment_EquipmentContainer, Equipment_OperationalLimitSet = Equipment_OperationalLimitSet, IdentifiedObject_mRID = IdentifiedObject_mRID, IdentifiedObject_name = IdentifiedObject_name, )
        # The ends of this power transformer. 
        self.PowerTransformer_PowerTransformerEnd = PowerTransformer_PowerTransformerEnd
    def add_PowerTransformer_PowerTransformerEnd(self, value: 'PowerTransformerEnd'):
        if not hasattr(self, 'PowerTransformer_PowerTransformerEnd'):
            self.__PowerTransformer_PowerTransformerEnd = []
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
        if list_objs == None:
            self.__PowerTransformer_PowerTransformerEnd = []
            return
        for obj in list_objs:
            self.add_PowerTransformer_PowerTransformerEnd(obj)
        if len(list_objs):
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
        if self.PowerTransformer_PowerTransformerEnd != []:
            for item in self.PowerTransformer_PowerTransformerEnd:
                ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}PowerTransformer.PowerTransformerEnd', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': item.URI})
        return root
    def validate(self):
        super().validate()
        minBound, maxBound = 1, float('Inf')
        if len(self.PowerTransformer_PowerTransformerEnd) < minBound or len(self.PowerTransformer_PowerTransformerEnd) > maxBound:
            raise ValueError('Incorrect multiplicity in PowerTransformer_PowerTransformerEnd [PowerTransformer]')
        if any(not isinstance(item, PowerTransformerEnd) for item in self.PowerTransformer_PowerTransformerEnd):
            raise ValueError(f'Incorrect datatype in PowerTransformer_PowerTransformerEnd [PowerTransformer] (expected PowerTransformerEnd but encountered {self.PowerTransformer_PowerTransformerEnd.__class__.__name__} instead)')
 
class Switch(ConductingEquipment):
    """A generic device designed to close, or open, or both, one or more electric circuits.  All switches are two terminal devices including grounding switches."""
    def __init__(self, Switch_normalOpen: bool = None, Switch_open: bool = None, ConductingEquipment_Terminals: List['Terminal'] = None, Equipment_EquipmentContainer: 'EquipmentContainer' = None, Equipment_OperationalLimitSet: List['OperationalLimitSet'] = None, IdentifiedObject_mRID: str = None, IdentifiedObject_name: str = None):
        super().__init__(ConductingEquipment_Terminals = ConductingEquipment_Terminals, Equipment_EquipmentContainer = Equipment_EquipmentContainer, Equipment_OperationalLimitSet = Equipment_OperationalLimitSet, IdentifiedObject_mRID = IdentifiedObject_mRID, IdentifiedObject_name = IdentifiedObject_name, )
        # The attribute is used in cases when no Measurement for the status value is present. If the Switch has a status measurement the Discrete.normalValue is expected to match with the Switch.normalOpen. 
        self.Switch_normalOpen = Switch_normalOpen
        # The attribute tells if the switch is considered open when used as input to topology processing. 
        self.Switch_open = Switch_open
    @property
    def Switch_normalOpen(self) -> bool:
        return self.__Switch_normalOpen
    @Switch_normalOpen.setter
    def Switch_normalOpen(self, value: bool):
        if value == None:
            self.__Switch_normalOpen = None
        elif not hasattr(self, 'Switch_normalOpen') or not self.Switch_normalOpen is value:
            self.__Switch_normalOpen = str(value).lower() == 'true' 
    @property
    def Switch_open(self) -> bool:
        return self.__Switch_open
    @Switch_open.setter
    def Switch_open(self, value: bool):
        if value == None:
            self.__Switch_open = None
        elif not hasattr(self, 'Switch_open') or not self.Switch_open is value:
            self.__Switch_open = str(value).lower() == 'true' 
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}Switch' 
        if self.Switch_normalOpen != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Switch.normalOpen')
            prop.text = str(self.Switch_normalOpen).lower()
        if self.Switch_open != None:
            prop = ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}Switch.open')
            prop.text = str(self.Switch_open).lower()
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.Switch_normalOpen, bool) and self.Switch_normalOpen != None:
            raise ValueError(f'Incorrect datatype in Switch_normalOpen [Switch] (expected bool but encountered {self.Switch_normalOpen.__class__.__name__} instead)')
        if not isinstance(self.Switch_open, bool) and self.Switch_open != None:
            raise ValueError(f'Incorrect datatype in Switch_open [Switch] (expected bool but encountered {self.Switch_open.__class__.__name__} instead)')
 
class ACLineSegment(Conductor):
    """A wire or combination of wires, with consistent electrical characteristics, building a single electrical system, used to carry alternating current between points in the power system.
For symmetrical, transposed 3ph lines, it is sufficient to use  attributes of the line segment, which describe impedances and admittances for the entire length of the segment.  Additionally impedances can be computed by using length and associated per length impedances.
The BaseVoltage at the two ends of ACLineSegments in a Line shall have the same BaseVoltage.nominalVoltage. However, boundary lines  may have slightly different BaseVoltage.nominalVoltages and  variation is allowed. Larger voltage difference in general requires use of an equivalent branch."""
    def __init__(self, ACLineSegment_PerLengthImpedance: 'PerLengthSequenceImpedance' = None, Conductor_length: 'Length' = None, ConductingEquipment_Terminals: List['Terminal'] = None, Equipment_EquipmentContainer: 'EquipmentContainer' = None, Equipment_OperationalLimitSet: List['OperationalLimitSet'] = None, IdentifiedObject_mRID: str = None, IdentifiedObject_name: str = None):
        super().__init__(Conductor_length = Conductor_length, ConductingEquipment_Terminals = ConductingEquipment_Terminals, Equipment_EquipmentContainer = Equipment_EquipmentContainer, Equipment_OperationalLimitSet = Equipment_OperationalLimitSet, IdentifiedObject_mRID = IdentifiedObject_mRID, IdentifiedObject_name = IdentifiedObject_name, )
        # Per-length impedance of this line segment. 
        self.ACLineSegment_PerLengthImpedance = ACLineSegment_PerLengthImpedance
    @property
    def ACLineSegment_PerLengthImpedance(self) -> 'PerLengthSequenceImpedance':
        return self.__ACLineSegment_PerLengthImpedance
    @ACLineSegment_PerLengthImpedance.setter
    def ACLineSegment_PerLengthImpedance(self, value: 'PerLengthSequenceImpedance'):
        if value == None:
            self.__ACLineSegment_PerLengthImpedance = None
        elif not hasattr(self, 'ACLineSegment_PerLengthImpedance') or not self.ACLineSegment_PerLengthImpedance is value:
            self.__ACLineSegment_PerLengthImpedance = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}ACLineSegment' 
        if self.ACLineSegment_PerLengthImpedance != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}ACLineSegment.PerLengthImpedance', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__ACLineSegment_PerLengthImpedance.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.ACLineSegment_PerLengthImpedance, PerLengthSequenceImpedance) and self.ACLineSegment_PerLengthImpedance != None:
            raise ValueError(f'Incorrect datatype in ACLineSegment_PerLengthImpedance [ACLineSegment] (expected PerLengthSequenceImpedance but encountered {self.ACLineSegment_PerLengthImpedance.__class__.__name__} instead)')
 
class BusbarSection(ConductingEquipment):
    """A conductor, or group of conductors, with negligible impedance, that serve to connect other conducting equipment within a single substation. 
Voltage measurements are typically obtained from VoltageTransformers that are connected to busbar sections. A bus bar section may have many physical terminals but for analysis is modelled with exactly one logical terminal."""
    def __init__(self, BusbarSection_ipMax: 'CurrentFlow' = None, ConductingEquipment_Terminals: List['Terminal'] = None, Equipment_EquipmentContainer: 'EquipmentContainer' = None, Equipment_OperationalLimitSet: List['OperationalLimitSet'] = None, IdentifiedObject_mRID: str = None, IdentifiedObject_name: str = None):
        super().__init__(ConductingEquipment_Terminals = ConductingEquipment_Terminals, Equipment_EquipmentContainer = Equipment_EquipmentContainer, Equipment_OperationalLimitSet = Equipment_OperationalLimitSet, IdentifiedObject_mRID = IdentifiedObject_mRID, IdentifiedObject_name = IdentifiedObject_name, )
        # Maximum allowable peak short-circuit current of busbar (Ipmax in the IEC 60909-0).  Mechanical limit of the busbar in the substation itself. Used for short circuit data exchange according to IEC 60909 
        self.BusbarSection_ipMax = BusbarSection_ipMax
    @property
    def BusbarSection_ipMax(self) -> 'CurrentFlow':
        return self.__BusbarSection_ipMax
    @BusbarSection_ipMax.setter
    def BusbarSection_ipMax(self, value: 'CurrentFlow'):
        if value == None:
            self.__BusbarSection_ipMax = None
        elif not hasattr(self, 'BusbarSection_ipMax') or not self.BusbarSection_ipMax is value:
            self.__BusbarSection_ipMax = value
    def serialize(self) -> ET.Element:
        self.validate()
        root = super().serialize()
        root.tag = '{grei.ufc.br/DistributionNetwork#}BusbarSection' 
        if self.BusbarSection_ipMax != None:
            ET.SubElement(root, '{grei.ufc.br/DistributionNetwork#}BusbarSection.ipMax', attrib={'{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource': self.__BusbarSection_ipMax.URI})
        return root
    def validate(self):
        super().validate()
        if not isinstance(self.BusbarSection_ipMax, CurrentFlow) and self.BusbarSection_ipMax != None:
            raise ValueError(f'Incorrect datatype in BusbarSection_ipMax [BusbarSection] (expected CurrentFlow but encountered {self.BusbarSection_ipMax.__class__.__name__} instead)')
