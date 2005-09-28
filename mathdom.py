#!/usr/bin/python

__all__ = ['MathDOM', 'MATHML_NAMESPACE_URI']

MATHML_NAMESPACE_URI = u"http://www.w3.org/1998/Math/MathML"

import sys, new, types, re
from itertools import chain

from xml.dom import Node, getDOMImplementation
from xml.dom.Element import Element
from xml.dom.ext import Print, PrettyPrint


UNARY_ARITHMETIC_FUNCTIONS = u"""
factorial minus abs conjugate arg real imaginary floor ceiling
"""

UNARY_LOGICAL_FUNCTIONS    = u"""
not
"""

UNARY_ELEMENTARY_CLASSICAL_FUNCTIONS = u"""
sin cos tan sec csc cot sinh cosh tanh sech csch coth
arcsin arccos arctan arccosh arccot arccoth arccsc arccsch
arcsec arcsech arcsinh arctanh exp ln log
"""

BINARY_ARITHMETIC_FUNCTIONS = u"""
quotient divide minus power rem
"""

NARY_ARITHMETIC_FUNCTIONS = u"""
plus times max min gcd lcm
"""

NARY_STATISTICAL_FUNCTIONS = u"""
mean sdev variance median mode
"""

NARY_LOGICAL_FUNCTIONS = u"""
and or xor
"""

NARY_FUNCTIONAL_FUNCTION = u"""
compose
"""

CONSTANTS = u"""
pi ExponentialE ee ImaginaryI ii gamma infin infty true false NotANumber NaN
"""

##

UNARY_FUNCTIONS  = UNARY_ELEMENTARY_CLASSICAL_FUNCTIONS + \
                   UNARY_ARITHMETIC_FUNCTIONS + \
                   UNARY_LOGICAL_FUNCTIONS

BINARY_FUNCTIONS = BINARY_ARITHMETIC_FUNCTIONS

NARY_FUNCTIONS   = NARY_ARITHMETIC_FUNCTIONS + \
                   NARY_STATISTICAL_FUNCTIONS + \
                   NARY_LOGICAL_FUNCTIONS + \
                   NARY_FUNCTIONAL_FUNCTION

##


METHODS_BY_ELEMENT_NAME = {}
def method_elements(element_names=u"", defined_in=u""):
    if defined_in:
        global_sources = globals()
        elements = frozenset(chain(
            element_names.split(),
            (name for s in defined_in.split() for name in global_sources[s].split())
            ))
    else:
        elements = frozenset(element_names.split())

    def register_function(function):
        new_function = (function.func_name, function)
        for element_name in elements:
            try:
                METHODS_BY_ELEMENT_NAME[element_name].append(new_function)
            except KeyError:
                METHODS_BY_ELEMENT_NAME[element_name] = [new_function]

    return register_function

# the same for all elements
def register_method(function):
    new_function = (function.func_name, function)
    try:
        METHODS_BY_ELEMENT_NAME[None].append(new_function)
    except KeyError:
        METHODS_BY_ELEMENT_NAME[None] = [new_function]


class MathElement(Element):
    "Fake class containing methods for different MathML Element objects."
    @register_method
    def mathtype(self):
        return self.localName

    @register_method
    def has_type(self, name):
        return self.localName == name

    @register_method
    def iteridentifiers(self):
        return (e.firstChild.data
                for e in self.getElementsByTagName(u'ci')
                if hasattr(e, 'firstChild') and hasattr(e.firstChild, 'data'))

    @register_method
    def iterconstants(self):
        return (e.firstChild.data
                for e in chain(self.getElementsByTagName(u'cn'), self.getElementsByTagName(u'name'))
                if hasattr(e, 'firstChild') and hasattr(e.firstChild, 'data'))

    @method_elements(u"apply")
    def operator(self):
        return self.firstChild

    @method_elements(u"apply")
    def operands(self):
        return self.childNodes[1:]

    @method_elements(u"apply")
    def append_operand(self, operand):
        if not self.childNodes:
            raise TypeError, "You must supply an operator first."
        self.childNodes.append(operand)

    @method_elements(defined_in="UNARY_FUNCTIONS")
    def operand(self):
        return self.firstChild

    @method_elements(u"minus")
    def is_negation(self):
        parent = self.parentNode
        children = parent.childNodes
        return len(children) == 2


class MathValue(Element):
    "Fake class containing methods for handling constants, identifiers, etc."
    @method_elements(u"ci")
    def value(self):
        return self.firstChild

    @method_elements(u"cn")
    def value(self):
        valuetype = self.valuetype()
        if valuetype == u'integer':
            return int(self.firstChild.data)
        elif valuetype == u'real':
            return float(self.firstChild.data)
        elif valuetype in (u'rational', u'e-notation'):
            return (self.childNodes[0].data, self.childNodes[2].data)
        elif valuetype == u'constant':
            value = self.firstChild.data.strip()
            return value.replace(u'&', '').replace(u';', '')

    @method_elements(u"cn")
    def valuetype(self):
        typeattr = self.getAttribute(u'type')
        if typeattr:
            return typeattr
        elif len(self.childNodes) == 1:
            value = self.firstChild.data
            for type_test, name in ((int, u'integer'), (float, u'real')):
                try:
                    type_test(value)
                    return name
                except ValueError:
                    pass
            
        return self.firstChild

    @method_elements(u"cn")
    def __repr__(self):
        name = self.localName
        return u"<%s type='%s'>%r</%s>" % (name, self.getAttribute('type') or 'real', self.value(), name)

    @method_elements(u"ci")
    def __repr__(self):
        name = self.localName
        return u"<%s>%r</%s>" % (name, self.firstChild, name)


#RE_ENTITY_REFERENCE = re.compile(r'^\s*&([a-z0-9]+);\s*$', re.I|re.U)
#MATCH_ENTITY = RE_ENTITY_REFERENCE.match
def augmentElements(node):
    "Weave methods into DOM Element objects."
    if node.nodeType == node.ELEMENT_NODE:
        element_methods = METHODS_BY_ELEMENT_NAME.get(node.localName, ())
        common_methods  = METHODS_BY_ELEMENT_NAME.get(None, ())
        for method_name, method in chain(element_methods, common_methods):
            new_method = new.instancemethod(method, node, Node)
            setattr(node, method_name, new_method)

    for child in tuple(node.childNodes):
        if child.nodeType == Node.TEXT_NODE:
            if not child.data.strip():
                node.removeChild(child)
                continue
##             else:
##                 entity_match = MATCH_ENTITY(child.data)
##                 if entity_match:
##                     print child.data
##                     entity_ref = node.ownerDocument.createEntityReference(entity_match.group(1))
##                     node.replaceChild(entity_ref, child)
        else:
            augmentElements(child)


# add qualifiers as attributes to standard DOM classes
DEFAULT_DICT = {}
def setupDefaults():
    dom_impl = getDOMImplementation()
    doc = dom_impl.createDocument(MATHML_NAMESPACE_URI, u"apply", None)

    logbase = doc.createElementNS(MATHML_NAMESPACE_URI, u'cn')
    logbase.appendChild( doc.createTextNode(u'10') )
    DEFAULT_DICT['logbase'] = logbase

setupDefaults()

class Qualifier(object):
    def __init__(self, name, valid_elements):
        self.name = name
        self.valid_elements = frozenset(valid_elements.split())
        self.__ACCESS_ERROR = "This element does not support the qualifier %s" % name

    def __find_qualifier(self, node):
        parent = node.parentNode
        if parent:
            ELEMENT_NODE = node.ELEMENT_NODE
            name = self.name
            for child in parent.childNodes:
                if child.nodeType == ELEMENT_NODE and child.localName == name:
                    return child
        return None

    def __get__(self, node, owner):
        if node is None:
            return self
        if node.localName not in self.valid_elements:
            raise NotImplementedError, self.__ACCESS_ERROR

        qualifier_node = self.__find_qualifier(node)
        if qualifier_node:
            return qualifier_node.firstChild
        else:
            return DEFAULT_DICT[self.name].cloneNode(True)

    def __set__(self, node, value):
        if node.localName not in self.valid_elements:
            raise NotImplementedError, self.__ACCESS_ERROR

        qualifier_node = self.__find_qualifier(node)
        if qualifier_node:
            for child in reversed(tuple(qualifier_node.children)):
                qualifier_node.removeChild(child)
        else:
            qualifier_node = node.ownerDocument.createElement(self.name)
            parent = node.parentNode
            parent.appendChild(qualifier_node)
        qualifier_node.appendChild(value)

Element.logbase = Qualifier('logbase', u'log')


class MathDOM(object):
    from xml.dom.ext.reader.Sax2 import Reader
    def __init__(self, document):
        augmentElements(document)
        self.__document = document

    @classmethod
    def fromMathmlString(cls, mathml):
        dom_builder = cls.Reader()
        return MathDOM( dom_builder.fromString(mathml) )

    @classmethod
    def fromMathmlFile(cls, input):
        dom_builder = cls.Reader()
        return MathDOM( dom_builder.fromStream(input) )

    @classmethod
    def fromMathmlSax(cls, input, sax_parser):
        dom_builder = cls.Reader(parser=sax_parser)
        return MathDOM( dom_builder.fromString(input) )

    def __getattr__(self, name):
        return getattr(self.__document, name)

    def __repr__(self):
        return repr(self.__document)

    def toMathml(self, out=sys.stdout, indent=False):
        if indent:
            PrettyPrint(self.__document, out)
        else:
            Print(self.__document, out)
