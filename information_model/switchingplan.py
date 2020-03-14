#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Generated Mon Feb  3 03:11:05 2020 by generateDS.py version 2.35.10.
# Python 3.7.3 | packaged by conda-forge | (default, Jul  1 2019, 22:01:29) [MSC v.1900 64 bit (AMD64)]
#
# Command line options:
#   ('-o', 'information_model\\switchingplan.py')
#   ('--export', 'write etree validate generator')
#
# Command line arguments:
#   D:\Documents\ESTUDO\Projetos\GREI\tcc\smad\..\artifacts\switchingplan.xsd
#
# Command line:
#   ..\python\generateDS\generateDS.py -o "information_model\switchingplan.py" --export="write etree validate generator" D:\Documents\ESTUDO\Projetos\GREI\tcc\smad\..\artifacts\switchingplan.xsd
#
# Current working directory (os.getcwd()):
#   smad
#

from six.moves import zip_longest
import os
import sys
import re as re_
import base64
import datetime as datetime_
import decimal as decimal_
try:
    from lxml import etree as etree_
except ImportError:
    from xml.etree import ElementTree as etree_


Validate_simpletypes_ = True
SaveElementTreeNode = True
if sys.version_info.major == 2:
    BaseStrType_ = basestring
else:
    BaseStrType_ = str


def parsexml_(infile, parser=None, **kwargs):
    if parser is None:
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        try:
            parser = etree_.ETCompatXMLParser()
        except AttributeError:
            # fallback to xml.etree
            parser = etree_.XMLParser()
    try:
        if isinstance(infile, os.PathLike):
            infile = os.path.join(infile)
    except AttributeError:
        pass
    doc = etree_.parse(infile, parser=parser, **kwargs)
    return doc

def parsexmlstring_(instring, parser=None, **kwargs):
    if parser is None:
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        try:
            parser = etree_.ETCompatXMLParser()
        except AttributeError:
            # fallback to xml.etree
            parser = etree_.XMLParser()
    element = etree_.fromstring(instring, parser=parser, **kwargs)
    return element

#
# Namespace prefix definition table (and other attributes, too)
#
# The module generatedsnamespaces, if it is importable, must contain
# a dictionary named GeneratedsNamespaceDefs.  This Python dictionary
# should map element type names (strings) to XML schema namespace prefix
# definitions.  The export method for any class for which there is
# a namespace prefix definition, will export that definition in the
# XML representation of that element.  See the export method of
# any generated element type class for an example of the use of this
# table.
# A sample table is:
#
#     # File: generatedsnamespaces.py
#
#     GenerateDSNamespaceDefs = {
#         "ElementtypeA": "http://www.xxx.com/namespaceA",
#         "ElementtypeB": "http://www.xxx.com/namespaceB",
#     }
#
# Additionally, the generatedsnamespaces module can contain a python
# dictionary named GenerateDSNamespaceTypePrefixes that associates element
# types with the namespace prefixes that are to be added to the
# "xsi:type" attribute value.  See the exportAttributes method of
# any generated element type and the generation of "xsi:type" for an
# example of the use of this table.
# An example table:
#
#     # File: generatedsnamespaces.py
#
#     GenerateDSNamespaceTypePrefixes = {
#         "ElementtypeC": "aaa:",
#         "ElementtypeD": "bbb:",
#     }
#

try:
    from generatedsnamespaces import GenerateDSNamespaceDefs as GenerateDSNamespaceDefs_
except ImportError:
    GenerateDSNamespaceDefs_ = {}
try:
    from generatedsnamespaces import GenerateDSNamespaceTypePrefixes as GenerateDSNamespaceTypePrefixes_
except ImportError:
    GenerateDSNamespaceTypePrefixes_ = {}

#
# You can replace the following class definition by defining an
# importable module named "generatedscollector" containing a class
# named "GdsCollector".  See the default class definition below for
# clues about the possible content of that class.
#
try:
    from generatedscollector import GdsCollector as GdsCollector_
except ImportError:

    class GdsCollector_(object):

        def __init__(self, messages=None):
            if messages is None:
                self.messages = []
            else:
                self.messages = messages

        def add_message(self, msg):
            self.messages.append(msg)

        def get_messages(self):
            return self.messages

        def clear_messages(self):
            self.messages = []

        def print_messages(self):
            for msg in self.messages:
                print("Warning: {}".format(msg))

        def write_messages(self, outstream):
            for msg in self.messages:
                outstream.write("Warning: {}\n".format(msg))


#
# The super-class for enum types
#

try:
    from enum import Enum
except ImportError:
    Enum = object

#
# The root super-class for element type classes
#
# Calls to the methods in these classes are generated by generateDS.py.
# You can replace these methods by re-implementing the following class
#   in a module named generatedssuper.py.

try:
    from generatedssuper import GeneratedsSuper
except ImportError as exp:
    
    class GeneratedsSuper(object):
        __hash__ = object.__hash__
        tzoff_pattern = re_.compile(r'(\+|-)((0\d|1[0-3]):[0-5]\d|14:00)$')
        class _FixedOffsetTZ(datetime_.tzinfo):
            def __init__(self, offset, name):
                self.__offset = datetime_.timedelta(minutes=offset)
                self.__name = name
            def utcoffset(self, dt):
                return self.__offset
            def tzname(self, dt):
                return self.__name
            def dst(self, dt):
                return None
        def gds_format_string(self, input_data, input_name=''):
            return input_data
        def gds_parse_string(self, input_data, node=None, input_name=''):
            return input_data
        def gds_validate_string(self, input_data, node=None, input_name=''):
            if not input_data:
                return ''
            else:
                return input_data
        def gds_format_base64(self, input_data, input_name=''):
            return base64.b64encode(input_data)
        def gds_validate_base64(self, input_data, node=None, input_name=''):
            return input_data
        def gds_format_integer(self, input_data, input_name=''):
            return '%d' % input_data
        def gds_parse_integer(self, input_data, node=None, input_name=''):
            try:
                ival = int(input_data)
            except (TypeError, ValueError) as exp:
                raise_parse_error(node, 'Requires integer value: %s' % exp)
            return ival
        def gds_validate_integer(self, input_data, node=None, input_name=''):
            try:
                value = int(input_data)
            except (TypeError, ValueError):
                raise_parse_error(node, 'Requires integer value')
            return value
        def gds_format_integer_list(self, input_data, input_name=''):
            return '%s' % ' '.join(input_data)
        def gds_validate_integer_list(
                self, input_data, node=None, input_name=''):
            values = input_data.split()
            for value in values:
                try:
                    int(value)
                except (TypeError, ValueError):
                    raise_parse_error(node, 'Requires sequence of integer valuess')
            return values
        def gds_format_float(self, input_data, input_name=''):
            return ('%.15f' % input_data).rstrip('0')
        def gds_parse_float(self, input_data, node=None, input_name=''):
            try:
                fval_ = float(input_data)
            except (TypeError, ValueError) as exp:
                raise_parse_error(node, 'Requires float or double value: %s' % exp)
            return fval_
        def gds_validate_float(self, input_data, node=None, input_name=''):
            try:
                value = float(input_data)
            except (TypeError, ValueError):
                raise_parse_error(node, 'Requires float value')
            return value
        def gds_format_float_list(self, input_data, input_name=''):
            return '%s' % ' '.join(input_data)
        def gds_validate_float_list(
                self, input_data, node=None, input_name=''):
            values = input_data.split()
            for value in values:
                try:
                    float(value)
                except (TypeError, ValueError):
                    raise_parse_error(node, 'Requires sequence of float values')
            return values
        def gds_format_decimal(self, input_data, input_name=''):
            return ('%0.10f' % input_data).rstrip('0')
        def gds_parse_decimal(self, input_data, node=None, input_name=''):
            try:
                decimal_value = decimal_.Decimal(input_data)
            except (TypeError, ValueError):
                raise_parse_error(node, 'Requires decimal value')
            return decimal_value
        def gds_validate_decimal(self, input_data, node=None, input_name=''):
            try:
                value = decimal_.Decimal(input_data)
            except (TypeError, ValueError):
                raise_parse_error(node, 'Requires decimal value')
            return value
        def gds_format_decimal_list(self, input_data, input_name=''):
            return '%s' % ' '.join(input_data)
        def gds_validate_decimal_list(
                self, input_data, node=None, input_name=''):
            values = input_data.split()
            for value in values:
                try:
                    decimal_.Decimal(value)
                except (TypeError, ValueError):
                    raise_parse_error(node, 'Requires sequence of decimal values')
            return values
        def gds_format_double(self, input_data, input_name=''):
            return '%e' % input_data
        def gds_parse_double(self, input_data, node=None, input_name=''):
            try:
                fval_ = float(input_data)
            except (TypeError, ValueError) as exp:
                raise_parse_error(node, 'Requires double or float value: %s' % exp)
            return fval_
        def gds_validate_double(self, input_data, node=None, input_name=''):
            try:
                value = float(input_data)
            except (TypeError, ValueError):
                raise_parse_error(node, 'Requires double or float value')
            return value
        def gds_format_double_list(self, input_data, input_name=''):
            return '%s' % ' '.join(input_data)
        def gds_validate_double_list(
                self, input_data, node=None, input_name=''):
            values = input_data.split()
            for value in values:
                try:
                    float(value)
                except (TypeError, ValueError):
                    raise_parse_error(
                        node, 'Requires sequence of double or float values')
            return values
        def gds_format_boolean(self, input_data, input_name=''):
            return ('%s' % input_data).lower()
        def gds_parse_boolean(self, input_data, node=None, input_name=''):
            if input_data in ('true', '1'):
                bval = True
            elif input_data in ('false', '0'):
                bval = False
            else:
                raise_parse_error(node, 'Requires boolean value')
            return bval
        def gds_validate_boolean(self, input_data, node=None, input_name=''):
            if input_data not in (True, 1, False, 0, ):
                raise_parse_error(
                    node,
                    'Requires boolean value '
                    '(one of True, 1, False, 0)')
            return input_data
        def gds_format_boolean_list(self, input_data, input_name=''):
            return '%s' % ' '.join(input_data)
        def gds_validate_boolean_list(
                self, input_data, node=None, input_name=''):
            values = input_data.split()
            for value in values:
                if value not in (True, 1, False, 0, ):
                    raise_parse_error(
                        node,
                        'Requires sequence of boolean values '
                        '(one of True, 1, False, 0)')
            return values
        def gds_validate_datetime(self, input_data, node=None, input_name=''):
            return input_data
        def gds_format_datetime(self, input_data, input_name=''):
            if input_data.microsecond == 0:
                _svalue = '%04d-%02d-%02dT%02d:%02d:%02d' % (
                    input_data.year,
                    input_data.month,
                    input_data.day,
                    input_data.hour,
                    input_data.minute,
                    input_data.second,
                )
            else:
                _svalue = '%04d-%02d-%02dT%02d:%02d:%02d.%s' % (
                    input_data.year,
                    input_data.month,
                    input_data.day,
                    input_data.hour,
                    input_data.minute,
                    input_data.second,
                    ('%f' % (float(input_data.microsecond) / 1000000))[2:],
                )
            if input_data.tzinfo is not None:
                tzoff = input_data.tzinfo.utcoffset(input_data)
                if tzoff is not None:
                    total_seconds = tzoff.seconds + (86400 * tzoff.days)
                    if total_seconds == 0:
                        _svalue += 'Z'
                    else:
                        if total_seconds < 0:
                            _svalue += '-'
                            total_seconds *= -1
                        else:
                            _svalue += '+'
                        hours = total_seconds // 3600
                        minutes = (total_seconds - (hours * 3600)) // 60
                        _svalue += '{0:02d}:{1:02d}'.format(hours, minutes)
            return _svalue
        @classmethod
        def gds_parse_datetime(cls, input_data):
            tz = None
            if input_data[-1] == 'Z':
                tz = GeneratedsSuper._FixedOffsetTZ(0, 'UTC')
                input_data = input_data[:-1]
            else:
                results = GeneratedsSuper.tzoff_pattern.search(input_data)
                if results is not None:
                    tzoff_parts = results.group(2).split(':')
                    tzoff = int(tzoff_parts[0]) * 60 + int(tzoff_parts[1])
                    if results.group(1) == '-':
                        tzoff *= -1
                    tz = GeneratedsSuper._FixedOffsetTZ(
                        tzoff, results.group(0))
                    input_data = input_data[:-6]
            time_parts = input_data.split('.')
            if len(time_parts) > 1:
                micro_seconds = int(float('0.' + time_parts[1]) * 1000000)
                input_data = '%s.%s' % (
                    time_parts[0], "{}".format(micro_seconds).rjust(6, "0"), )
                dt = datetime_.datetime.strptime(
                    input_data, '%Y-%m-%dT%H:%M:%S.%f')
            else:
                dt = datetime_.datetime.strptime(
                    input_data, '%Y-%m-%dT%H:%M:%S')
            dt = dt.replace(tzinfo=tz)
            return dt
        def gds_validate_date(self, input_data, node=None, input_name=''):
            return input_data
        def gds_format_date(self, input_data, input_name=''):
            _svalue = '%04d-%02d-%02d' % (
                input_data.year,
                input_data.month,
                input_data.day,
            )
            try:
                if input_data.tzinfo is not None:
                    tzoff = input_data.tzinfo.utcoffset(input_data)
                    if tzoff is not None:
                        total_seconds = tzoff.seconds + (86400 * tzoff.days)
                        if total_seconds == 0:
                            _svalue += 'Z'
                        else:
                            if total_seconds < 0:
                                _svalue += '-'
                                total_seconds *= -1
                            else:
                                _svalue += '+'
                            hours = total_seconds // 3600
                            minutes = (total_seconds - (hours * 3600)) // 60
                            _svalue += '{0:02d}:{1:02d}'.format(
                                hours, minutes)
            except AttributeError:
                pass
            return _svalue
        @classmethod
        def gds_parse_date(cls, input_data):
            tz = None
            if input_data[-1] == 'Z':
                tz = GeneratedsSuper._FixedOffsetTZ(0, 'UTC')
                input_data = input_data[:-1]
            else:
                results = GeneratedsSuper.tzoff_pattern.search(input_data)
                if results is not None:
                    tzoff_parts = results.group(2).split(':')
                    tzoff = int(tzoff_parts[0]) * 60 + int(tzoff_parts[1])
                    if results.group(1) == '-':
                        tzoff *= -1
                    tz = GeneratedsSuper._FixedOffsetTZ(
                        tzoff, results.group(0))
                    input_data = input_data[:-6]
            dt = datetime_.datetime.strptime(input_data, '%Y-%m-%d')
            dt = dt.replace(tzinfo=tz)
            return dt.date()
        def gds_validate_time(self, input_data, node=None, input_name=''):
            return input_data
        def gds_format_time(self, input_data, input_name=''):
            if input_data.microsecond == 0:
                _svalue = '%02d:%02d:%02d' % (
                    input_data.hour,
                    input_data.minute,
                    input_data.second,
                )
            else:
                _svalue = '%02d:%02d:%02d.%s' % (
                    input_data.hour,
                    input_data.minute,
                    input_data.second,
                    ('%f' % (float(input_data.microsecond) / 1000000))[2:],
                )
            if input_data.tzinfo is not None:
                tzoff = input_data.tzinfo.utcoffset(input_data)
                if tzoff is not None:
                    total_seconds = tzoff.seconds + (86400 * tzoff.days)
                    if total_seconds == 0:
                        _svalue += 'Z'
                    else:
                        if total_seconds < 0:
                            _svalue += '-'
                            total_seconds *= -1
                        else:
                            _svalue += '+'
                        hours = total_seconds // 3600
                        minutes = (total_seconds - (hours * 3600)) // 60
                        _svalue += '{0:02d}:{1:02d}'.format(hours, minutes)
            return _svalue
        def gds_validate_simple_patterns(self, patterns, target):
            # pat is a list of lists of strings/patterns.
            # The target value must match at least one of the patterns
            # in order for the test to succeed.
            found1 = True
            for patterns1 in patterns:
                found2 = False
                for patterns2 in patterns1:
                    mo = re_.search(patterns2, target)
                    if mo is not None and len(mo.group(0)) == len(target):
                        found2 = True
                        break
                if not found2:
                    found1 = False
                    break
            return found1
        @classmethod
        def gds_parse_time(cls, input_data):
            tz = None
            if input_data[-1] == 'Z':
                tz = GeneratedsSuper._FixedOffsetTZ(0, 'UTC')
                input_data = input_data[:-1]
            else:
                results = GeneratedsSuper.tzoff_pattern.search(input_data)
                if results is not None:
                    tzoff_parts = results.group(2).split(':')
                    tzoff = int(tzoff_parts[0]) * 60 + int(tzoff_parts[1])
                    if results.group(1) == '-':
                        tzoff *= -1
                    tz = GeneratedsSuper._FixedOffsetTZ(
                        tzoff, results.group(0))
                    input_data = input_data[:-6]
            if len(input_data.split('.')) > 1:
                dt = datetime_.datetime.strptime(input_data, '%H:%M:%S.%f')
            else:
                dt = datetime_.datetime.strptime(input_data, '%H:%M:%S')
            dt = dt.replace(tzinfo=tz)
            return dt.time()
        def gds_check_cardinality_(
                self, value, input_name,
                min_occurs=0, max_occurs=1, required=None):
            if value is None:
                length = 0
            elif isinstance(value, list):
                length = len(value)
            else:
                length = 1
            if required is not None :
                if required and length < 1:
                    self.gds_collector_.add_message(
                        "Required value {}{} is missing".format(
                            input_name, self.gds_get_node_lineno_()))
            if length < min_occurs:
                self.gds_collector_.add_message(
                    "Number of values for {}{} is below "
                    "the minimum allowed, "
                    "expected at least {}, found {}".format(
                        input_name, self.gds_get_node_lineno_(),
                        min_occurs, length))
            elif length > max_occurs:
                self.gds_collector_.add_message(
                    "Number of values for {}{} is above "
                    "the maximum allowed, "
                    "expected at most {}, found {}".format(
                        input_name, self.gds_get_node_lineno_(),
                        max_occurs, length))
        def gds_validate_builtin_ST_(
                self, validator, value, input_name,
                min_occurs=None, max_occurs=None, required=None):
            if value is not None:
                try:
                    validator(value, input_name=input_name)
                except GDSParseError as parse_error:
                    self.gds_collector_.add_message(str(parse_error))
        def gds_validate_defined_ST_(
                self, validator, value, input_name,
                min_occurs=None, max_occurs=None, required=None):
            if value is not None:
                try:
                    validator(value)
                except GDSParseError as parse_error:
                    self.gds_collector_.add_message(str(parse_error))
        def gds_str_lower(self, instring):
            return instring.lower()
        def get_path_(self, node):
            path_list = []
            self.get_path_list_(node, path_list)
            path_list.reverse()
            path = '/'.join(path_list)
            return path
        Tag_strip_pattern_ = re_.compile(r'\{.*\}')
        def get_path_list_(self, node, path_list):
            if node is None:
                return
            tag = GeneratedsSuper.Tag_strip_pattern_.sub('', node.tag)
            if tag:
                path_list.append(tag)
            self.get_path_list_(node.getparent(), path_list)
        def get_class_obj_(self, node, default_class=None):
            class_obj1 = default_class
            if 'xsi' in node.nsmap:
                classname = node.get('{%s}type' % node.nsmap['xsi'])
                if classname is not None:
                    names = classname.split(':')
                    if len(names) == 2:
                        classname = names[1]
                    class_obj2 = globals().get(classname)
                    if class_obj2 is not None:
                        class_obj1 = class_obj2
            return class_obj1
        def gds_build_any(self, node, type_name=None):
            # provide default value in case option --disable-xml is used.
            content = ""
            content = etree_.tostring(node, encoding="unicode")
            return content
        @classmethod
        def gds_reverse_node_mapping(cls, mapping):
            return dict(((v, k) for k, v in mapping.items()))
        @staticmethod
        def gds_encode(instring):
            if sys.version_info.major == 2:
                if ExternalEncoding:
                    encoding = ExternalEncoding
                else:
                    encoding = 'utf-8'
                return instring.encode(encoding)
            else:
                return instring
        @staticmethod
        def convert_unicode(instring):
            if isinstance(instring, str):
                result = quote_xml(instring)
            elif sys.version_info.major == 2 and isinstance(instring, unicode):
                result = quote_xml(instring).encode('utf8')
            else:
                result = GeneratedsSuper.gds_encode(str(instring))
            return result
        def __eq__(self, other):
            def excl_select_objs_(obj):
                return (obj[0] != 'parent_object_' and
                        obj[0] != 'gds_collector_')
            if type(self) != type(other):
                return False
            return all(x == y for x, y in zip_longest(
                filter(excl_select_objs_, self.__dict__.items()),
                filter(excl_select_objs_, other.__dict__.items())))
        def __ne__(self, other):
            return not self.__eq__(other)
        # Django ETL transform hooks.
        def gds_djo_etl_transform(self):
            pass
        def gds_djo_etl_transform_db_obj(self, dbobj):
            pass
        # SQLAlchemy ETL transform hooks.
        def gds_sqa_etl_transform(self):
            return 0, None
        def gds_sqa_etl_transform_db_obj(self, dbobj):
            pass
        def gds_get_node_lineno_(self):
            if (hasattr(self, "gds_elementtree_node_") and
                    self.gds_elementtree_node_ is not None):
                return ' near line {}'.format(
                    self.gds_elementtree_node_.sourceline)
            else:
                return ""
    
    
    def getSubclassFromModule_(module, class_):
        '''Get the subclass of a class from a specific module.'''
        name = class_.__name__ + 'Sub'
        if hasattr(module, name):
            return getattr(module, name)
        else:
            return None


#
# If you have installed IPython you can uncomment and use the following.
# IPython is available from http://ipython.scipy.org/.
#

## from IPython.Shell import IPShellEmbed
## args = ''
## ipshell = IPShellEmbed(args,
##     banner = 'Dropping into IPython',
##     exit_msg = 'Leaving Interpreter, back to program.')

# Then use the following line where and when you want to drop into the
# IPython shell:
#    ipshell('<some message> -- Entering ipshell.\nHit Ctrl-D to exit')

#
# Globals
#

ExternalEncoding = ''
# Set this to false in order to deactivate during export, the use of
# name space prefixes captured from the input document.
UseCapturedNS_ = True
CapturedNsmap_ = {}
Tag_pattern_ = re_.compile(r'({.*})?(.*)')
String_cleanup_pat_ = re_.compile(r"[\n\r\s]+")
Namespace_extract_pat_ = re_.compile(r'{(.*)}(.*)')
CDATA_pattern_ = re_.compile(r"<!\[CDATA\[.*?\]\]>", re_.DOTALL)

# Change this to redirect the generated superclass module to use a
# specific subclass module.
CurrentSubclassModule_ = None

#
# Support/utility functions.
#


def showIndent(outfile, level, pretty_print=True):
    if pretty_print:
        for idx in range(level):
            outfile.write('    ')


def quote_xml(inStr):
    "Escape markup chars, but do not modify CDATA sections."
    if not inStr:
        return ''
    s1 = (isinstance(inStr, BaseStrType_) and inStr or '%s' % inStr)
    s2 = ''
    pos = 0
    matchobjects = CDATA_pattern_.finditer(s1)
    for mo in matchobjects:
        s3 = s1[pos:mo.start()]
        s2 += quote_xml_aux(s3)
        s2 += s1[mo.start():mo.end()]
        pos = mo.end()
    s3 = s1[pos:]
    s2 += quote_xml_aux(s3)
    return s2


def quote_xml_aux(inStr):
    s1 = inStr.replace('&', '&amp;')
    s1 = s1.replace('<', '&lt;')
    s1 = s1.replace('>', '&gt;')
    return s1


def quote_attrib(inStr):
    s1 = (isinstance(inStr, BaseStrType_) and inStr or '%s' % inStr)
    s1 = s1.replace('&', '&amp;')
    s1 = s1.replace('<', '&lt;')
    s1 = s1.replace('>', '&gt;')
    if '"' in s1:
        if "'" in s1:
            s1 = '"%s"' % s1.replace('"', "&quot;")
        else:
            s1 = "'%s'" % s1
    else:
        s1 = '"%s"' % s1
    return s1


def quote_python(inStr):
    s1 = inStr
    if s1.find("'") == -1:
        if s1.find('\n') == -1:
            return "'%s'" % s1
        else:
            return "'''%s'''" % s1
    else:
        if s1.find('"') != -1:
            s1 = s1.replace('"', '\\"')
        if s1.find('\n') == -1:
            return '"%s"' % s1
        else:
            return '"""%s"""' % s1


def get_all_text_(node):
    if node.text is not None:
        text = node.text
    else:
        text = ''
    for child in node:
        if child.tail is not None:
            text += child.tail
    return text


def find_attr_value_(attr_name, node):
    attrs = node.attrib
    attr_parts = attr_name.split(':')
    value = None
    if len(attr_parts) == 1:
        value = attrs.get(attr_name)
    elif len(attr_parts) == 2:
        prefix, name = attr_parts
        namespace = node.nsmap.get(prefix)
        if namespace is not None:
            value = attrs.get('{%s}%s' % (namespace, name, ))
    return value


def encode_str_2_3(instr):
    return instr


class GDSParseError(Exception):
    pass


def raise_parse_error(node, msg):
    if node is not None:
        msg = '%s (element %s/line %d)' % (msg, node.tag, node.sourceline, )
    raise GDSParseError(msg)


class MixedContainer:
    # Constants for category:
    CategoryNone = 0
    CategoryText = 1
    CategorySimple = 2
    CategoryComplex = 3
    # Constants for content_type:
    TypeNone = 0
    TypeText = 1
    TypeString = 2
    TypeInteger = 3
    TypeFloat = 4
    TypeDecimal = 5
    TypeDouble = 6
    TypeBoolean = 7
    TypeBase64 = 8
    def __init__(self, category, content_type, name, value):
        self.category = category
        self.content_type = content_type
        self.name = name
        self.value = value
    def getCategory(self):
        return self.category
    def getContenttype(self, content_type):
        return self.content_type
    def getValue(self):
        return self.value
    def getName(self):
        return self.name
    def export(self, outfile, level, name, namespace,
               pretty_print=True):
        if self.category == MixedContainer.CategoryText:
            # Prevent exporting empty content as empty lines.
            if self.value.strip():
                outfile.write(self.value)
        elif self.category == MixedContainer.CategorySimple:
            self.exportSimple(outfile, level, name)
        else:    # category == MixedContainer.CategoryComplex
            self.value.export(
                outfile, level, namespace, name_=name,
                pretty_print=pretty_print)
    def exportSimple(self, outfile, level, name):
        if self.content_type == MixedContainer.TypeString:
            outfile.write('<%s>%s</%s>' % (
                self.name, self.value, self.name))
        elif self.content_type == MixedContainer.TypeInteger or \
                self.content_type == MixedContainer.TypeBoolean:
            outfile.write('<%s>%d</%s>' % (
                self.name, self.value, self.name))
        elif self.content_type == MixedContainer.TypeFloat or \
                self.content_type == MixedContainer.TypeDecimal:
            outfile.write('<%s>%f</%s>' % (
                self.name, self.value, self.name))
        elif self.content_type == MixedContainer.TypeDouble:
            outfile.write('<%s>%g</%s>' % (
                self.name, self.value, self.name))
        elif self.content_type == MixedContainer.TypeBase64:
            outfile.write('<%s>%s</%s>' % (
                self.name,
                base64.b64encode(self.value),
                self.name))
    def to_etree(self, element):
        if self.category == MixedContainer.CategoryText:
            # Prevent exporting empty content as empty lines.
            if self.value.strip():
                if len(element) > 0:
                    if element[-1].tail is None:
                        element[-1].tail = self.value
                    else:
                        element[-1].tail += self.value
                else:
                    if element.text is None:
                        element.text = self.value
                    else:
                        element.text += self.value
        elif self.category == MixedContainer.CategorySimple:
            subelement = etree_.SubElement(
                element, '%s' % self.name)
            subelement.text = self.to_etree_simple()
        else:    # category == MixedContainer.CategoryComplex
            self.value.to_etree(element)
    def to_etree_simple(self):
        if self.content_type == MixedContainer.TypeString:
            text = self.value
        elif (self.content_type == MixedContainer.TypeInteger or
                self.content_type == MixedContainer.TypeBoolean):
            text = '%d' % self.value
        elif (self.content_type == MixedContainer.TypeFloat or
                self.content_type == MixedContainer.TypeDecimal):
            text = '%f' % self.value
        elif self.content_type == MixedContainer.TypeDouble:
            text = '%g' % self.value
        elif self.content_type == MixedContainer.TypeBase64:
            text = '%s' % base64.b64encode(self.value)
        return text
    def exportLiteral(self, outfile, level, name):
        if self.category == MixedContainer.CategoryText:
            showIndent(outfile, level)
            outfile.write(
                'model_.MixedContainer(%d, %d, "%s", "%s"),\n' % (
                    self.category, self.content_type,
                    self.name, self.value))
        elif self.category == MixedContainer.CategorySimple:
            showIndent(outfile, level)
            outfile.write(
                'model_.MixedContainer(%d, %d, "%s", "%s"),\n' % (
                    self.category, self.content_type,
                    self.name, self.value))
        else:    # category == MixedContainer.CategoryComplex
            showIndent(outfile, level)
            outfile.write(
                'model_.MixedContainer(%d, %d, "%s",\n' % (
                    self.category, self.content_type, self.name,))
            self.value.exportLiteral(outfile, level + 1)
            showIndent(outfile, level)
            outfile.write(')\n')


class MemberSpec_(object):
    def __init__(self, name='', data_type='', container=0,
            optional=0, child_attrs=None, choice=None):
        self.name = name
        self.data_type = data_type
        self.container = container
        self.child_attrs = child_attrs
        self.choice = choice
        self.optional = optional
    def set_name(self, name): self.name = name
    def get_name(self): return self.name
    def set_data_type(self, data_type): self.data_type = data_type
    def get_data_type_chain(self): return self.data_type
    def get_data_type(self):
        if isinstance(self.data_type, list):
            if len(self.data_type) > 0:
                return self.data_type[-1]
            else:
                return 'xs:string'
        else:
            return self.data_type
    def set_container(self, container): self.container = container
    def get_container(self): return self.container
    def set_child_attrs(self, child_attrs): self.child_attrs = child_attrs
    def get_child_attrs(self): return self.child_attrs
    def set_choice(self, choice): self.choice = choice
    def get_choice(self): return self.choice
    def set_optional(self, optional): self.optional = optional
    def get_optional(self): return self.optional


def _cast(typ, value):
    if typ is None or value is None:
        return value
    return typ(value)

#
# Data representation classes.
#


class Analog_Meas(Enum):
    CURRENT_MAGNITUDE='CurrentMagnitude'
    CURRENT_PHASE='CurrentPhase'


class Breaker_DiscreteMeasAlias(Enum):
    FALSE='False'
    TRUE='True'
    INVALID='Invalid'
    OPEN='Open'
    CLOSE='Close'
    INTERMEDIATE='Intermediate'


class Discrete_Meas(Enum):
    BREAKER_POSITION='BreakerPosition'
    BREAKER_FAILURE='BreakerFailure'


class PhaseCode(Enum):
    """An unordered enumeration of phase identifiers. Allows designation of
    phases for both transmission and distribution equipment, circuits and
    loads. The enumeration, by itself, does not describe how the phases are
    connected together or connected to ground. Ground is not explicitly
    denoted as a phase.
    Residential and small commercial loads are often served from single-phase,
    or split-phase, secondary circuits. For example of s12N, phases 1 and 2
    refer to hot wires that are 180 degrees out of phase, while N refers to
    the neutral wire. Through single-phase transformer connections, these
    secondary circuits may be served from one or two of the primary phases
    A, B, and C. For three-phase loads, use the A, B, C phase codes instead
    of s12N."""
    A='A' # Phase A.
    B='B' # Phase B.
    C='C' # Phase C.
    N='N' # Neutral phase.
    AB='AB' # Phases A and B.
    AC='AC' # Phases A and C.
    BC='BC' # Phases B and C.
    AN='AN' # Phases A and neutral.
    BN='BN' # Phases B and neutral.
    CN='CN' # Phases C and neutral.


class Purpose(Enum):
    COORDINATION='Coordination'
    ISOLATION='Isolation'
    RESTORATION='Restoration'


class ReportName(Enum):
    FAULT_REPORT='FaultReport'
    RESTORATION_REPORT='RestorationReport'


class SwitchActionKind(Enum):
    """Kind of action on switch."""
    OPEN='open' # Open the switch.
    CLOSE='close' # Close the switch.
    DISABLE_RECLOSING='disableReclosing' # Disable (automatic) switch reclosing.
    ENABLE_RECLOSING='enableReclosing' # Enable (automatic) switch reclosing.


class UnitMultiplier(Enum):
    """The unit multipliers defined for the CIM. When applied to unit symbols
    that already contain a multiplier, both multipliers are used. For
    example, to exchange kilograms using unit symbol of kg, one uses the
    "none" multiplier, to exchange metric ton (Mg), one uses the "k"
    multiplier."""
    NONE='none' # No multiplier or equivalently multiply by 1.
    MICRO='micro' # Micro 10**-6.
    M='m' # Milli 10**-3.
    K='k' # Kilo 10**3.
    M_1='M' # Mega 10**6.
    G='G' # Giga 10**9.


class UnitSymbol(Enum):
    """The units defined for usage in the CIM."""
    A='A' # Current in Ampere.
    DEG='deg' # Plane angle in degrees.
    RAD='rad' # Plane angle in radian (m/m).
    W='W' # Real power in Watt (J/s). Electrical power may have real and reactive components. The real portion of electrical power (I²R or VIcos(phi)), is expressed in Watts. (See also apparent power and reactive power.)
    VA='VA' # Apparent power in Volt Ampere (See also real power and reactive power.)
    V_AR='VAr' # Reactive power in Volt Ampere reactive. The “reactive” or “imaginary” component of electrical power (VIsin(phi)). (See also real power and apparent power). Note: Different meter designs use different methods to arrive at their results. Some meters may compute reactive power as an arithmetic value, while others compute the value vectorially. The data consumer should determine the method in use and the suitability of the measurement for the intended purpose.


class ProtectedSwitch(GeneratedsSuper):
    """A ProtectedSwitch is a switching device that can be operated by
    ProtectionEquipment."""
    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None
    def __init__(self, mRID=None, name=None, normalOpen=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        self.mRID = mRID
        self.mRID_nsprefix_ = None
        self.name = name
        self.name_nsprefix_ = None
        self.normalOpen = normalOpen
        self.normalOpen_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, ProtectedSwitch)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if ProtectedSwitch.subclass:
            return ProtectedSwitch.subclass(*args_, **kwargs_)
        else:
            return ProtectedSwitch(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_mRID(self):
        return self.mRID
    def set_mRID(self, mRID):
        self.mRID = mRID
    def get_name(self):
        return self.name
    def set_name(self, name):
        self.name = name
    def get_normalOpen(self):
        return self.normalOpen
    def set_normalOpen(self, normalOpen):
        self.normalOpen = normalOpen
    def hasContent_(self):
        if (
            self.mRID is not None or
            self.name is not None or
            self.normalOpen is not None
        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='xmlns:smad="grei.ufc.br/smad"', name_='ProtectedSwitch', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('ProtectedSwitch')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self.exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='ProtectedSwitch')
        if self.hasContent_():
            outfile.write('>%s' % (eol_, ))
            self.exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='ProtectedSwitch', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='ProtectedSwitch'):
        pass
    def exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='xmlns:smad="grei.ufc.br/smad"', name_='ProtectedSwitch', fromsubclass_=False, pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.mRID is not None:
            namespaceprefix_ = self.mRID_nsprefix_ + ':' if (UseCapturedNS_ and self.mRID_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%smRID>%s</%smRID>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.mRID), input_name='mRID')), namespaceprefix_ , eol_))
        if self.name is not None:
            namespaceprefix_ = self.name_nsprefix_ + ':' if (UseCapturedNS_ and self.name_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sname>%s</%sname>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.name), input_name='name')), namespaceprefix_ , eol_))
        if self.normalOpen is not None:
            namespaceprefix_ = self.normalOpen_nsprefix_ + ':' if (UseCapturedNS_ and self.normalOpen_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%snormalOpen>%s</%snormalOpen>%s' % (namespaceprefix_ , self.gds_format_boolean(self.normalOpen, input_name='normalOpen'), namespaceprefix_ , eol_))
    def to_etree(self, parent_element=None, name_='ProtectedSwitch', mapping_=None):
        if parent_element is None:
            element = etree_.Element('{grei.ufc.br/smad}' + name_)
        else:
            element = etree_.SubElement(parent_element, '{grei.ufc.br/smad}' + name_)
        if self.mRID is not None:
            mRID_ = self.mRID
            etree_.SubElement(element, '{grei.ufc.br/smad}mRID').text = self.gds_format_string(mRID_)
        if self.name is not None:
            name_ = self.name
            etree_.SubElement(element, '{grei.ufc.br/smad}name').text = self.gds_format_string(name_)
        if self.normalOpen is not None:
            normalOpen_ = self.normalOpen
            etree_.SubElement(element, '{grei.ufc.br/smad}normalOpen').text = self.gds_format_boolean(normalOpen_)
        if mapping_ is not None:
            mapping_[id(self)] = element
        return element
    def validate_(self, gds_collector, recursive=False):
        self.gds_collector_ = gds_collector
        message_count = len(self.gds_collector_.get_messages())
        # validate simple type attributes
        # validate simple type children
        self.gds_validate_builtin_ST_(self.gds_validate_string, self.mRID, 'mRID')
        self.gds_check_cardinality_(self.mRID, 'mRID', min_occurs=1, max_occurs=1)
        self.gds_validate_builtin_ST_(self.gds_validate_string, self.name, 'name')
        self.gds_check_cardinality_(self.name, 'name', min_occurs=0, max_occurs=1)
        self.gds_validate_builtin_ST_(self.gds_validate_boolean, self.normalOpen, 'normalOpen')
        self.gds_check_cardinality_(self.normalOpen, 'normalOpen', min_occurs=0, max_occurs=1)
        # validate complex type children
        if recursive:
            pass
        return message_count == len(self.gds_collector_.get_messages())
    def generateRecursively_(self, level=0):
        yield (self, level)
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self.buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def buildAttributes(self, node, attrs, already_processed):
        pass
    def buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        if nodeName_ == 'mRID':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'mRID')
            value_ = self.gds_validate_string(value_, node, 'mRID')
            self.mRID = value_
            self.mRID_nsprefix_ = child_.prefix
        elif nodeName_ == 'name':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'name')
            value_ = self.gds_validate_string(value_, node, 'name')
            self.name = value_
            self.name_nsprefix_ = child_.prefix
        elif nodeName_ == 'normalOpen':
            sval_ = child_.text
            ival_ = self.gds_parse_boolean(sval_, node, 'normalOpen')
            ival_ = self.gds_validate_boolean(ival_, node, 'normalOpen')
            self.normalOpen = ival_
            self.normalOpen_nsprefix_ = child_.prefix
# end class ProtectedSwitch


class SwitchAction(GeneratedsSuper):
    """Action on switch as a switching step."""
    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None
    def __init__(self, kind=None, sequenceNumber=None, isFreeSequence=None, plannedDateTime=None, executedDateTime=None, issuedDateTime=None, OperatedSwitch=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        self.kind = kind
        self.validate_SwitchActionKind(self.kind)
        self.kind_nsprefix_ = None
        self.sequenceNumber = sequenceNumber
        self.sequenceNumber_nsprefix_ = None
        self.isFreeSequence = isFreeSequence
        self.isFreeSequence_nsprefix_ = None
        if isinstance(plannedDateTime, BaseStrType_):
            initvalue_ = datetime_.datetime.strptime(plannedDateTime, '%Y-%m-%dT%H:%M:%S')
        else:
            initvalue_ = plannedDateTime
        self.plannedDateTime = initvalue_
        self.plannedDateTime_nsprefix_ = None
        if isinstance(executedDateTime, BaseStrType_):
            initvalue_ = datetime_.datetime.strptime(executedDateTime, '%Y-%m-%dT%H:%M:%S')
        else:
            initvalue_ = executedDateTime
        self.executedDateTime = initvalue_
        self.executedDateTime_nsprefix_ = None
        if isinstance(issuedDateTime, BaseStrType_):
            initvalue_ = datetime_.datetime.strptime(issuedDateTime, '%Y-%m-%dT%H:%M:%S')
        else:
            initvalue_ = issuedDateTime
        self.issuedDateTime = initvalue_
        self.issuedDateTime_nsprefix_ = None
        self.OperatedSwitch = OperatedSwitch
        self.OperatedSwitch_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, SwitchAction)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if SwitchAction.subclass:
            return SwitchAction.subclass(*args_, **kwargs_)
        else:
            return SwitchAction(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_kind(self):
        return self.kind
    def set_kind(self, kind):
        self.kind = kind
    def get_sequenceNumber(self):
        return self.sequenceNumber
    def set_sequenceNumber(self, sequenceNumber):
        self.sequenceNumber = sequenceNumber
    def get_isFreeSequence(self):
        return self.isFreeSequence
    def set_isFreeSequence(self, isFreeSequence):
        self.isFreeSequence = isFreeSequence
    def get_plannedDateTime(self):
        return self.plannedDateTime
    def set_plannedDateTime(self, plannedDateTime):
        self.plannedDateTime = plannedDateTime
    def get_executedDateTime(self):
        return self.executedDateTime
    def set_executedDateTime(self, executedDateTime):
        self.executedDateTime = executedDateTime
    def get_issuedDateTime(self):
        return self.issuedDateTime
    def set_issuedDateTime(self, issuedDateTime):
        self.issuedDateTime = issuedDateTime
    def get_OperatedSwitch(self):
        return self.OperatedSwitch
    def set_OperatedSwitch(self, OperatedSwitch):
        self.OperatedSwitch = OperatedSwitch
    def validate_SwitchActionKind(self, value):
        result = True
        # Validate type SwitchActionKind, a restriction on xsd:string.
        if value is not None and Validate_simpletypes_ and self.gds_collector_ is not None:
            if not isinstance(value, str):
                lineno = self.gds_get_node_lineno_()
                self.gds_collector_.add_message('Value "%(value)s"%(lineno)s is not of the correct base simple type (str)' % {"value": value, "lineno": lineno, })
                return False
            value = value
            enumerations = ['open', 'close', 'disableReclosing', 'enableReclosing']
            if value not in enumerations:
                lineno = self.gds_get_node_lineno_()
                self.gds_collector_.add_message('Value "%(value)s"%(lineno)s does not match xsd enumeration restriction on SwitchActionKind' % {"value" : encode_str_2_3(value), "lineno": lineno} )
                result = False
        return result
    def hasContent_(self):
        if (
            self.kind is not None or
            self.sequenceNumber is not None or
            self.isFreeSequence is not None or
            self.plannedDateTime is not None or
            self.executedDateTime is not None or
            self.issuedDateTime is not None or
            self.OperatedSwitch is not None
        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='xmlns:smad="grei.ufc.br/smad"', name_='SwitchAction', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('SwitchAction')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self.exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='SwitchAction')
        if self.hasContent_():
            outfile.write('>%s' % (eol_, ))
            self.exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='SwitchAction', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='SwitchAction'):
        pass
    def exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='xmlns:smad="grei.ufc.br/smad"', name_='SwitchAction', fromsubclass_=False, pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.kind is not None:
            namespaceprefix_ = self.kind_nsprefix_ + ':' if (UseCapturedNS_ and self.kind_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%skind>%s</%skind>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.kind), input_name='kind')), namespaceprefix_ , eol_))
        if self.sequenceNumber is not None:
            namespaceprefix_ = self.sequenceNumber_nsprefix_ + ':' if (UseCapturedNS_ and self.sequenceNumber_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%ssequenceNumber>%s</%ssequenceNumber>%s' % (namespaceprefix_ , self.gds_format_integer(self.sequenceNumber, input_name='sequenceNumber'), namespaceprefix_ , eol_))
        if self.isFreeSequence is not None:
            namespaceprefix_ = self.isFreeSequence_nsprefix_ + ':' if (UseCapturedNS_ and self.isFreeSequence_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sisFreeSequence>%s</%sisFreeSequence>%s' % (namespaceprefix_ , self.gds_format_boolean(self.isFreeSequence, input_name='isFreeSequence'), namespaceprefix_ , eol_))
        if self.plannedDateTime is not None:
            namespaceprefix_ = self.plannedDateTime_nsprefix_ + ':' if (UseCapturedNS_ and self.plannedDateTime_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%splannedDateTime>%s</%splannedDateTime>%s' % (namespaceprefix_ , self.gds_format_datetime(self.plannedDateTime, input_name='plannedDateTime'), namespaceprefix_ , eol_))
        if self.executedDateTime is not None:
            namespaceprefix_ = self.executedDateTime_nsprefix_ + ':' if (UseCapturedNS_ and self.executedDateTime_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sexecutedDateTime>%s</%sexecutedDateTime>%s' % (namespaceprefix_ , self.gds_format_datetime(self.executedDateTime, input_name='executedDateTime'), namespaceprefix_ , eol_))
        if self.issuedDateTime is not None:
            namespaceprefix_ = self.issuedDateTime_nsprefix_ + ':' if (UseCapturedNS_ and self.issuedDateTime_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sissuedDateTime>%s</%sissuedDateTime>%s' % (namespaceprefix_ , self.gds_format_datetime(self.issuedDateTime, input_name='issuedDateTime'), namespaceprefix_ , eol_))
        if self.OperatedSwitch is not None:
            namespaceprefix_ = self.OperatedSwitch_nsprefix_ + ':' if (UseCapturedNS_ and self.OperatedSwitch_nsprefix_) else ''
            self.OperatedSwitch.export(outfile, level, namespaceprefix_, namespacedef_='', name_='OperatedSwitch', pretty_print=pretty_print)
    def to_etree(self, parent_element=None, name_='SwitchAction', mapping_=None):
        if parent_element is None:
            element = etree_.Element('{grei.ufc.br/smad}' + name_)
        else:
            element = etree_.SubElement(parent_element, '{grei.ufc.br/smad}' + name_)
        if self.kind is not None:
            kind_ = self.kind
            etree_.SubElement(element, '{grei.ufc.br/smad}kind').text = self.gds_format_string(kind_)
        if self.sequenceNumber is not None:
            sequenceNumber_ = self.sequenceNumber
            etree_.SubElement(element, '{grei.ufc.br/smad}sequenceNumber').text = self.gds_format_integer(sequenceNumber_)
        if self.isFreeSequence is not None:
            isFreeSequence_ = self.isFreeSequence
            etree_.SubElement(element, '{grei.ufc.br/smad}isFreeSequence').text = self.gds_format_boolean(isFreeSequence_)
        if self.plannedDateTime is not None:
            plannedDateTime_ = self.plannedDateTime
            etree_.SubElement(element, '{grei.ufc.br/smad}plannedDateTime').text = self.gds_format_datetime(plannedDateTime_)
        if self.executedDateTime is not None:
            executedDateTime_ = self.executedDateTime
            etree_.SubElement(element, '{grei.ufc.br/smad}executedDateTime').text = self.gds_format_datetime(executedDateTime_)
        if self.issuedDateTime is not None:
            issuedDateTime_ = self.issuedDateTime
            etree_.SubElement(element, '{grei.ufc.br/smad}issuedDateTime').text = self.gds_format_datetime(issuedDateTime_)
        if self.OperatedSwitch is not None:
            OperatedSwitch_ = self.OperatedSwitch
            OperatedSwitch_.to_etree(element, name_='OperatedSwitch', mapping_=mapping_)
        if mapping_ is not None:
            mapping_[id(self)] = element
        return element
    def validate_(self, gds_collector, recursive=False):
        self.gds_collector_ = gds_collector
        message_count = len(self.gds_collector_.get_messages())
        # validate simple type attributes
        # validate simple type children
        self.gds_validate_defined_ST_(self.validate_SwitchActionKind, self.kind, 'kind')
        self.gds_check_cardinality_(self.kind, 'kind', min_occurs=1, max_occurs=1)
        self.gds_validate_builtin_ST_(self.gds_validate_integer, self.sequenceNumber, 'sequenceNumber')
        self.gds_check_cardinality_(self.sequenceNumber, 'sequenceNumber', min_occurs=0, max_occurs=1)
        self.gds_validate_builtin_ST_(self.gds_validate_boolean, self.isFreeSequence, 'isFreeSequence')
        self.gds_check_cardinality_(self.isFreeSequence, 'isFreeSequence', min_occurs=0, max_occurs=1)
        self.gds_validate_builtin_ST_(self.gds_validate_datetime, self.plannedDateTime, 'plannedDateTime')
        self.gds_check_cardinality_(self.plannedDateTime, 'plannedDateTime', min_occurs=0, max_occurs=1)
        self.gds_validate_builtin_ST_(self.gds_validate_datetime, self.executedDateTime, 'executedDateTime')
        self.gds_check_cardinality_(self.executedDateTime, 'executedDateTime', min_occurs=0, max_occurs=1)
        self.gds_validate_builtin_ST_(self.gds_validate_datetime, self.issuedDateTime, 'issuedDateTime')
        self.gds_check_cardinality_(self.issuedDateTime, 'issuedDateTime', min_occurs=0, max_occurs=1)
        # validate complex type children
        self.gds_check_cardinality_(self.OperatedSwitch, 'OperatedSwitch', min_occurs=1, max_occurs=1)
        if recursive:
            self.OperatedSwitch.validate_(gds_collector, recursive=True)
        return message_count == len(self.gds_collector_.get_messages())
    def generateRecursively_(self, level=0):
        yield (self, level)
        # generate complex type children
        level += 1
        yield from self.OperatedSwitch.generateRecursively_(level)
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self.buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def buildAttributes(self, node, attrs, already_processed):
        pass
    def buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        if nodeName_ == 'kind':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'kind')
            value_ = self.gds_validate_string(value_, node, 'kind')
            self.kind = value_
            self.kind_nsprefix_ = child_.prefix
            # validate type SwitchActionKind
            self.validate_SwitchActionKind(self.kind)
        elif nodeName_ == 'sequenceNumber' and child_.text:
            sval_ = child_.text
            ival_ = self.gds_parse_integer(sval_, node, 'sequenceNumber')
            ival_ = self.gds_validate_integer(ival_, node, 'sequenceNumber')
            self.sequenceNumber = ival_
            self.sequenceNumber_nsprefix_ = child_.prefix
        elif nodeName_ == 'isFreeSequence':
            sval_ = child_.text
            ival_ = self.gds_parse_boolean(sval_, node, 'isFreeSequence')
            ival_ = self.gds_validate_boolean(ival_, node, 'isFreeSequence')
            self.isFreeSequence = ival_
            self.isFreeSequence_nsprefix_ = child_.prefix
        elif nodeName_ == 'plannedDateTime':
            sval_ = child_.text
            dval_ = self.gds_parse_datetime(sval_)
            self.plannedDateTime = dval_
            self.plannedDateTime_nsprefix_ = child_.prefix
        elif nodeName_ == 'executedDateTime':
            sval_ = child_.text
            dval_ = self.gds_parse_datetime(sval_)
            self.executedDateTime = dval_
            self.executedDateTime_nsprefix_ = child_.prefix
        elif nodeName_ == 'issuedDateTime':
            sval_ = child_.text
            dval_ = self.gds_parse_datetime(sval_)
            self.issuedDateTime = dval_
            self.issuedDateTime_nsprefix_ = child_.prefix
        elif nodeName_ == 'OperatedSwitch':
            obj_ = ProtectedSwitch.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.OperatedSwitch = obj_
            obj_.original_tagname_ = 'OperatedSwitch'
# end class SwitchAction


class SwitchingPlan_Type(GeneratedsSuper):
    """A sequence of grouped or atomic steps intended to:
    - de-energise equipment or part of the network for safe work, and/or
    - bring back in service previously de-energised equipment or part of the
    network."""
    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None
    def __init__(self, mRID=None, name=None, purpose=None, createdDateTime=None, SwitchAction=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        self.mRID = mRID
        self.mRID_nsprefix_ = None
        self.name = name
        self.name_nsprefix_ = None
        self.purpose = purpose
        self.validate_Purpose(self.purpose)
        self.purpose_nsprefix_ = None
        if isinstance(createdDateTime, BaseStrType_):
            initvalue_ = datetime_.datetime.strptime(createdDateTime, '%Y-%m-%dT%H:%M:%S')
        else:
            initvalue_ = createdDateTime
        self.createdDateTime = initvalue_
        self.createdDateTime_nsprefix_ = None
        if SwitchAction is None:
            self.SwitchAction = []
        else:
            self.SwitchAction = SwitchAction
        self.SwitchAction_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, SwitchingPlan_Type)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if SwitchingPlan_Type.subclass:
            return SwitchingPlan_Type.subclass(*args_, **kwargs_)
        else:
            return SwitchingPlan_Type(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_mRID(self):
        return self.mRID
    def set_mRID(self, mRID):
        self.mRID = mRID
    def get_name(self):
        return self.name
    def set_name(self, name):
        self.name = name
    def get_purpose(self):
        return self.purpose
    def set_purpose(self, purpose):
        self.purpose = purpose
    def get_createdDateTime(self):
        return self.createdDateTime
    def set_createdDateTime(self, createdDateTime):
        self.createdDateTime = createdDateTime
    def get_SwitchAction(self):
        return self.SwitchAction
    def set_SwitchAction(self, SwitchAction):
        self.SwitchAction = SwitchAction
    def add_SwitchAction(self, value):
        self.SwitchAction.append(value)
    def insert_SwitchAction_at(self, index, value):
        self.SwitchAction.insert(index, value)
    def replace_SwitchAction_at(self, index, value):
        self.SwitchAction[index] = value
    def validate_Purpose(self, value):
        result = True
        # Validate type Purpose, a restriction on xsd:string.
        if value is not None and Validate_simpletypes_ and self.gds_collector_ is not None:
            if not isinstance(value, str):
                lineno = self.gds_get_node_lineno_()
                self.gds_collector_.add_message('Value "%(value)s"%(lineno)s is not of the correct base simple type (str)' % {"value": value, "lineno": lineno, })
                return False
            value = value
            enumerations = ['Coordination', 'Isolation', 'Restoration']
            if value not in enumerations:
                lineno = self.gds_get_node_lineno_()
                self.gds_collector_.add_message('Value "%(value)s"%(lineno)s does not match xsd enumeration restriction on Purpose' % {"value" : encode_str_2_3(value), "lineno": lineno} )
                result = False
        return result
    def hasContent_(self):
        if (
            self.mRID is not None or
            self.name is not None or
            self.purpose is not None or
            self.createdDateTime is not None or
            self.SwitchAction
        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='xmlns:smad="grei.ufc.br/smad"', name_='SwitchingPlan_Type', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('SwitchingPlan_Type')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self.exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='SwitchingPlan_Type')
        if self.hasContent_():
            outfile.write('>%s' % (eol_, ))
            self.exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='SwitchingPlan_Type', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='SwitchingPlan_Type'):
        pass
    def exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='xmlns:smad="grei.ufc.br/smad"', name_='SwitchingPlan_Type', fromsubclass_=False, pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.mRID is not None:
            namespaceprefix_ = self.mRID_nsprefix_ + ':' if (UseCapturedNS_ and self.mRID_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%smRID>%s</%smRID>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.mRID), input_name='mRID')), namespaceprefix_ , eol_))
        if self.name is not None:
            namespaceprefix_ = self.name_nsprefix_ + ':' if (UseCapturedNS_ and self.name_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sname>%s</%sname>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.name), input_name='name')), namespaceprefix_ , eol_))
        if self.purpose is not None:
            namespaceprefix_ = self.purpose_nsprefix_ + ':' if (UseCapturedNS_ and self.purpose_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%spurpose>%s</%spurpose>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.purpose), input_name='purpose')), namespaceprefix_ , eol_))
        if self.createdDateTime is not None:
            namespaceprefix_ = self.createdDateTime_nsprefix_ + ':' if (UseCapturedNS_ and self.createdDateTime_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%screatedDateTime>%s</%screatedDateTime>%s' % (namespaceprefix_ , self.gds_format_datetime(self.createdDateTime, input_name='createdDateTime'), namespaceprefix_ , eol_))
        for SwitchAction_ in self.SwitchAction:
            namespaceprefix_ = self.SwitchAction_nsprefix_ + ':' if (UseCapturedNS_ and self.SwitchAction_nsprefix_) else ''
            SwitchAction_.export(outfile, level, namespaceprefix_, namespacedef_='', name_='SwitchAction', pretty_print=pretty_print)
    def to_etree(self, parent_element=None, name_='SwitchingPlan_Type', mapping_=None):
        if parent_element is None:
            element = etree_.Element('{grei.ufc.br/smad}' + name_)
        else:
            element = etree_.SubElement(parent_element, '{grei.ufc.br/smad}' + name_)
        if self.mRID is not None:
            mRID_ = self.mRID
            etree_.SubElement(element, '{grei.ufc.br/smad}mRID').text = self.gds_format_string(mRID_)
        if self.name is not None:
            name_ = self.name
            etree_.SubElement(element, '{grei.ufc.br/smad}name').text = self.gds_format_string(name_)
        if self.purpose is not None:
            purpose_ = self.purpose
            etree_.SubElement(element, '{grei.ufc.br/smad}purpose').text = self.gds_format_string(purpose_)
        if self.createdDateTime is not None:
            createdDateTime_ = self.createdDateTime
            etree_.SubElement(element, '{grei.ufc.br/smad}createdDateTime').text = self.gds_format_datetime(createdDateTime_)
        for SwitchAction_ in self.SwitchAction:
            SwitchAction_.to_etree(element, name_='SwitchAction', mapping_=mapping_)
        if mapping_ is not None:
            mapping_[id(self)] = element
        return element
    def validate_(self, gds_collector, recursive=False):
        self.gds_collector_ = gds_collector
        message_count = len(self.gds_collector_.get_messages())
        # validate simple type attributes
        # validate simple type children
        self.gds_validate_builtin_ST_(self.gds_validate_string, self.mRID, 'mRID')
        self.gds_check_cardinality_(self.mRID, 'mRID', min_occurs=1, max_occurs=1)
        self.gds_validate_builtin_ST_(self.gds_validate_string, self.name, 'name')
        self.gds_check_cardinality_(self.name, 'name', min_occurs=0, max_occurs=1)
        self.gds_validate_defined_ST_(self.validate_Purpose, self.purpose, 'purpose')
        self.gds_check_cardinality_(self.purpose, 'purpose', min_occurs=0, max_occurs=1)
        self.gds_validate_builtin_ST_(self.gds_validate_datetime, self.createdDateTime, 'createdDateTime')
        self.gds_check_cardinality_(self.createdDateTime, 'createdDateTime', min_occurs=0, max_occurs=1)
        # validate complex type children
        self.gds_check_cardinality_(self.SwitchAction, 'SwitchAction', min_occurs=1, max_occurs=9999999)
        if recursive:
            for item in self.SwitchAction:
                item.validate_(gds_collector, recursive=True)
        return message_count == len(self.gds_collector_.get_messages())
    def generateRecursively_(self, level=0):
        yield (self, level)
        # generate complex type children
        level += 1
        yield from self.SwitchAction.generateRecursively_(level)
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self.buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def buildAttributes(self, node, attrs, already_processed):
        pass
    def buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        if nodeName_ == 'mRID':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'mRID')
            value_ = self.gds_validate_string(value_, node, 'mRID')
            self.mRID = value_
            self.mRID_nsprefix_ = child_.prefix
        elif nodeName_ == 'name':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'name')
            value_ = self.gds_validate_string(value_, node, 'name')
            self.name = value_
            self.name_nsprefix_ = child_.prefix
        elif nodeName_ == 'purpose':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'purpose')
            value_ = self.gds_validate_string(value_, node, 'purpose')
            self.purpose = value_
            self.purpose_nsprefix_ = child_.prefix
            # validate type Purpose
            self.validate_Purpose(self.purpose)
        elif nodeName_ == 'createdDateTime':
            sval_ = child_.text
            dval_ = self.gds_parse_datetime(sval_)
            self.createdDateTime = dval_
            self.createdDateTime_nsprefix_ = child_.prefix
        elif nodeName_ == 'SwitchAction':
            obj_ = SwitchAction.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.SwitchAction.append(obj_)
            obj_.original_tagname_ = 'SwitchAction'
# end class SwitchingPlan_Type


class Breaker_DiscreteMeasValue(GeneratedsSuper):
    """An integer number. The range is unspecified and not limited."""
    __hash__ = GeneratedsSuper.__hash__
    subclass = None
    superclass = None
    def __init__(self, valueOf_=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        self.valueOf_ = valueOf_
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, Breaker_DiscreteMeasValue)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if Breaker_DiscreteMeasValue.subclass:
            return Breaker_DiscreteMeasValue.subclass(*args_, **kwargs_)
        else:
            return Breaker_DiscreteMeasValue(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_valueOf_(self): return self.valueOf_
    def set_valueOf_(self, valueOf_): self.valueOf_ = valueOf_
    def hasContent_(self):
        if (
            (1 if type(self.valueOf_) in [int,float] else self.valueOf_)
        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='smad:', namespacedef_='xmlns:smad="grei.ufc.br/smad"', name_='Breaker_DiscreteMeasValue', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('Breaker_DiscreteMeasValue')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self.exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='Breaker_DiscreteMeasValue')
        if self.hasContent_():
            outfile.write('>')
            outfile.write(self.convert_unicode(self.valueOf_))
            self.exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='Breaker_DiscreteMeasValue', pretty_print=pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def exportAttributes(self, outfile, level, already_processed, namespaceprefix_='smad:', name_='Breaker_DiscreteMeasValue'):
        pass
    def exportChildren(self, outfile, level, namespaceprefix_='smad:', namespacedef_='xmlns:smad="grei.ufc.br/smad"', name_='Breaker_DiscreteMeasValue', fromsubclass_=False, pretty_print=True):
        pass
    def to_etree(self, parent_element=None, name_='Breaker_DiscreteMeasValue', mapping_=None):
        if parent_element is None:
            element = etree_.Element('{grei.ufc.br/smad}' + name_)
        else:
            element = etree_.SubElement(parent_element, '{grei.ufc.br/smad}' + name_)
        if self.hasContent_():
            element.text = self.gds_format_string(self.get_valueOf_())
        if mapping_ is not None:
            mapping_[id(self)] = element
        return element
    def validate_(self, gds_collector, recursive=False):
        self.gds_collector_ = gds_collector
        message_count = len(self.gds_collector_.get_messages())
        # validate simple type attributes
        # validate simple type children
        # validate complex type children
        if recursive:
            pass
        return message_count == len(self.gds_collector_.get_messages())
    def generateRecursively_(self, level=0):
        yield (self, level)
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self.buildAttributes(node, node.attrib, already_processed)
        self.valueOf_ = get_all_text_(node)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def buildAttributes(self, node, attrs, already_processed):
        pass
    def buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        pass
# end class Breaker_DiscreteMeasValue


GDSClassesMapping = {
    'SwitchingPlan': SwitchingPlan_Type,
}


USAGE_TEXT = """
Usage: python <Parser>.py [ -s ] <in_xml_file>
"""


def usage():
    print(USAGE_TEXT)
    sys.exit(1)


def get_root_tag(node):
    tag = Tag_pattern_.match(node.tag).groups()[-1]
    rootClass = GDSClassesMapping.get(tag)
    if rootClass is None:
        rootClass = globals().get(tag)
    return tag, rootClass


def get_required_ns_prefix_defs(rootNode):
    '''Get all name space prefix definitions required in this XML doc.
    Return a dictionary of definitions and a char string of definitions.
    '''
    nsmap = {
        prefix: uri
        for node in rootNode.iter()
        for (prefix, uri) in node.nsmap.items()
        if prefix is not None
    }
    namespacedefs = ' '.join([
        'xmlns:{}="{}"'.format(prefix, uri)
        for prefix, uri in nsmap.items()
    ])
    return nsmap, namespacedefs


def parse(inFileName, silence=False, print_warnings=True):
    global CapturedNsmap_
    gds_collector = GdsCollector_()
    parser = None
    doc = parsexml_(inFileName, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'SwitchingPlan_Type'
        rootClass = SwitchingPlan_Type
    rootObj = rootClass.factory()
    rootObj.build(rootNode, gds_collector_=gds_collector)
    CapturedNsmap_, namespacedefs = get_required_ns_prefix_defs(rootNode)
    if not SaveElementTreeNode:
        doc = None
        rootNode = None
    if not silence:
        sys.stdout.write('<?xml version="1.0" ?>\n')
        rootObj.export(
            sys.stdout, 0, name_=rootTag,
            namespacedef_=namespacedefs,
            pretty_print=True)
    if print_warnings and len(gds_collector.get_messages()) > 0:
        separator = ('-' * 50) + '\n'
        sys.stderr.write(separator)
        sys.stderr.write('----- Warnings -- count: {} -----\n'.format(
            len(gds_collector.get_messages()), ))
        gds_collector.write_messages(sys.stderr)
        sys.stderr.write(separator)
    return rootObj


def parseEtree(inFileName, silence=False, print_warnings=True):
    parser = None
    doc = parsexml_(inFileName, parser)
    gds_collector = GdsCollector_()
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'SwitchingPlan_Type'
        rootClass = SwitchingPlan_Type
    rootObj = rootClass.factory()
    rootObj.build(rootNode, gds_collector_=gds_collector)
    # Enable Python to collect the space used by the DOM.
    mapping = {}
    rootElement = rootObj.to_etree(None, name_=rootTag, mapping_=mapping)
    reverse_mapping = rootObj.gds_reverse_node_mapping(mapping)
    if not SaveElementTreeNode:
        doc = None
        rootNode = None
    if not silence:
        content = etree_.tostring(
            rootElement, pretty_print=True,
            xml_declaration=True, encoding="utf-8")
        sys.stdout.write(str(content))
        sys.stdout.write('\n')
    if print_warnings and len(gds_collector.get_messages()) > 0:
        separator = ('-' * 50) + '\n'
        sys.stderr.write(separator)
        sys.stderr.write('----- Warnings -- count: {} -----\n'.format(
            len(gds_collector.get_messages()), ))
        gds_collector.write_messages(sys.stderr)
        sys.stderr.write(separator)
    return rootObj, rootElement, mapping, reverse_mapping


def parseString(inString, silence=False, print_warnings=True):
    '''Parse a string, create the object tree, and export it.

    Arguments:
    - inString -- A string.  This XML fragment should not start
      with an XML declaration containing an encoding.
    - silence -- A boolean.  If False, export the object.
    Returns -- The root object in the tree.
    '''
    parser = None
    rootNode= parsexmlstring_(inString, parser)
    gds_collector = GdsCollector_()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'SwitchingPlan_Type'
        rootClass = SwitchingPlan_Type
    rootObj = rootClass.factory()
    rootObj.build(rootNode, gds_collector_=gds_collector)
    if not SaveElementTreeNode:
        rootNode = None
    if not silence:
        sys.stdout.write('<?xml version="1.0" ?>\n')
        rootObj.export(
            sys.stdout, 0, name_=rootTag,
            namespacedef_='xmlns:smad="grei.ufc.br/smad"')
    if print_warnings and len(gds_collector.get_messages()) > 0:
        separator = ('-' * 50) + '\n'
        sys.stderr.write(separator)
        sys.stderr.write('----- Warnings -- count: {} -----\n'.format(
            len(gds_collector.get_messages()), ))
        gds_collector.write_messages(sys.stderr)
        sys.stderr.write(separator)
    return rootObj


def parseLiteral(inFileName, silence=False, print_warnings=True):
    parser = None
    doc = parsexml_(inFileName, parser)
    gds_collector = GdsCollector_()
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'SwitchingPlan_Type'
        rootClass = SwitchingPlan_Type
    rootObj = rootClass.factory()
    rootObj.build(rootNode, gds_collector_=gds_collector)
    # Enable Python to collect the space used by the DOM.
    if not SaveElementTreeNode:
        doc = None
        rootNode = None
    if not silence:
        sys.stdout.write('#from switchingplan import *\n\n')
        sys.stdout.write('import switchingplan as model_\n\n')
        sys.stdout.write('rootObj = model_.rootClass(\n')
        rootObj.exportLiteral(sys.stdout, 0, name_=rootTag)
        sys.stdout.write(')\n')
    if print_warnings and len(gds_collector.get_messages()) > 0:
        separator = ('-' * 50) + '\n'
        sys.stderr.write(separator)
        sys.stderr.write('----- Warnings -- count: {} -----\n'.format(
            len(gds_collector.get_messages()), ))
        gds_collector.write_messages(sys.stderr)
        sys.stderr.write(separator)
    return rootObj


def main():
    args = sys.argv[1:]
    if len(args) == 1:
        parse(args[0])
    else:
        usage()


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    main()

RenameMappings_ = {
}

__all__ = [
    "Breaker_DiscreteMeasValue",
    "ProtectedSwitch",
    "SwitchAction",
    "SwitchingPlan_Type"
]
