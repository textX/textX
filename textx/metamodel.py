#######################################################################
# Name: metamodel.py
# Purpose: Meta-model construction.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################
from collections import namedtuple

from .textx import language_from_str, python_type, BASE_TYPE_NAMES
from .const import MULT_ONE, MULT_ZEROORMORE, MULT_ONEORMORE, RULE_NORMAL


class MetaAttr(object):
    """
    A metaclass for attribute description.

    Attributes:
        name(str): Attribute name.
        cls(str, TextXClass or base python type): The type of the attribute.
        mult(str): Multiplicity
        cont(bool): Is this attribute contained inside object.
        ref(bool): Is this attribute a reference. If it is not a reference it must
            be containment.
        position(int): A position in the input string where attribute is defined.
    """
    def __init__(self, name, cls=None, mult=MULT_ONE, cont=True, ref=False, position=0):
        self.name = name
        self.cls = cls
        self.mult = mult
        self.cont = cont
        self.ref = ref
        self.position = position


class TextXClass(object):
    """Base class for all language classes."""
    pass


class TextXMetaModel(dict):
    """
    Metamodel contains all information about language abstract syntax.
    Furthermore, this class is in charge for model instantiation and new
    language class creation.
    This class inherites dictionary as is used for language class lookup.

    Attributes:
        rootcls(TextXClass): A language class that is a root of the metamodel.
    """

    def __init__(self):
        self.rootcls = None

    def new_class(self, name, position, inherits=None, root=False):
        """
        Creates a new class with the given name.
        Args:
            name(str): The name of the class.
            positon(int): A position in the input where class is defined.
            root(bool): Is this class a root class of the metamodel.
        """

        class Meta(TextXClass):
            """
            Dynamic metaclass. Each textX rule will result in creating
            one Meta class with the type name of the rule.
            Model is a graph of python instances of this metaclasses.
            """
            # Attribute information (MetaAttr instances)
            _attrs = {}

            # Inheriting classes
            _inh_by = inherits if inherits else []

            _position = position
            _type = RULE_NORMAL

            def __init__(self):
                """
                Initializes attributes.
                """
                for attr in self._attrs.values():
                    if attr.mult in [MULT_ZEROORMORE, MULT_ONEORMORE]:
                        # list
                        setattr(self, attr.name, [])
                    elif attr.cls.__name__ in BASE_TYPE_NAMES:
                        # Instantiate base python type
                        setattr(self, attr.name, python_type(attr.cls.__name__)())
                    else:
                        # Reference to other obj
                        setattr(self, attr.name, None)

            @classmethod
            def new_attr(clazz, name, cls=None, mult=MULT_ONE, cont=True,
                    ref=False, position=0):
                """Creates new meta attribute of this class."""
                attr = MetaAttr(name, cls, mult, cont, ref, position)
                clazz._attrs[name] = attr
                return attr

            # def __str__(self):
            #     return str_indent(self)

        cls = Meta
        cls.__name__ = name

        self[name] = cls

        if root:
            self.rootcls = cls

        return cls

    def model_from_str(self, model_str):
        """
        Instantiates model from the given string.
        """
        return self.parser.get_model_from_str(model_str)

    def model_from_file(self, file_name):
        """
        Instantiates model from the given file.
        """
        return self.parser.get_model_from_file(file_name)


def metamodel_from_str(lang_desc, debug=False):
    """
    Creates a new metamodel from the textX description given as a string.
    """
    metamodel = TextXMetaModel()

    # Base types hierarchy
    ID = metamodel.new_class('ID', 0)
    STRING = metamodel.new_class('STRING', 0)
    BOOL = metamodel.new_class('BOOL', 0)
    INT = metamodel.new_class('INT', 0)
    FLOAT = metamodel.new_class('FLOAT', 0)
    Number = metamodel.new_class('NUMBER', 0, [INT, FLOAT])
    metamodel.new_class('BASETYPE', 0, [Number, ID, STRING, BOOL])

    language_from_str(lang_desc, metamodel, debug=debug)

    return metamodel


def metamodel_from_file(file_name, debug=False):
    """
    Creates new metamodel from the given file.
    """
    with open(file_name, 'r') as f:
        lang_desc = f.read()

    metamodel = metamodel_from_str(lang_desc, debug)

    return metamodel


