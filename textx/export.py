# -*- coding: utf-8 -*-
#######################################################################
# Name: export.py
# Purpose: Export of textX based models and metamodels to dot file
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014-2016 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################
from __future__ import unicode_literals
from arpeggio import Match, OrderedChoice, Sequence, OneOrMore, ZeroOrMore,\
    Optional, SyntaxPredicate
from .const import MULT_ZEROORMORE, MULT_ONEORMORE, MULT_ONE, RULE_ABSTRACT, \
    RULE_COMMON
from .textx import PRIMITIVE_PYTHON_TYPES, BASE_TYPE_NAMES
import codecs
import sys
if sys.version < '3':
    text = unicode
else:
    text = str


HEADER = '''
    digraph xtext {
    fontname = "Bitstream Vera Sans"
    fontsize = 8
    node[
        shape=record,
        style=filled,
        fillcolor=aliceblue
    ]
    nodesep = 0.3
    edge[dir=black,arrowtail=empty]


'''

def match_str(cls):
    """
    For a given match rule meta-class returns a nice string representation.
    """
    def r(s):
        if s.root and s.rule_name in BASE_TYPE_NAMES:
            return s.rule_name
        else:
            if isinstance(s, Match):
                result = text(s)
            elif isinstance(s, OrderedChoice):
                result = "|".join([r(x) for x in s.nodes])
            elif isinstance(s, Sequence):
                result = " ".join([r(x) for x in s.nodes])
            elif isinstance(s, ZeroOrMore):
                result = "({})*".format(r(s.nodes[0]))
            elif isinstance(s, OneOrMore):
                result =  "({})+".format(r(s.nodes[0]))
            elif isinstance(s, Optional):
                result =  "{}?".format(r(s.nodes[0]))
            elif isinstance(s, SyntaxPredicate):
                result =  ""
            return "{}{}".format(result, "-" if s.suppress else "")

    mstr = ""
    if cls.__name__ not in BASE_TYPE_NAMES and \
            not (cls._tx_type is RULE_ABSTRACT and
                 cls.__name__ != cls._tx_peg_rule.rule_name):
        e = cls._tx_peg_rule
        if isinstance(e, OrderedChoice):
            mstr = "|".join([r(x) for x in e.nodes
                             if x.rule_name in BASE_TYPE_NAMES or not x.root])
        elif isinstance(e, Sequence):
            mstr = " ".join([r(x) for x in e.nodes])
        else:
            mstr = r(e)

        mstr = dot_escape(mstr)

    return mstr

def dot_escape(s):
    return s.replace('\n', r'\n')\
            .replace('\\', '\\\\')\
            .replace('"', r'\"')\
            .replace('|', r'\|')\
            .replace('{', r'\{')\
            .replace('}', r'\}')\
            .replace('?', r'\?')


def metamodel_export(metamodel, file_name):

    with codecs.open(file_name, 'w', encoding="utf-8") as f:
        f.write(HEADER)

        for cls in metamodel:
            name = cls.__name__
            attrs = ""
            if cls._tx_type is not RULE_COMMON:
                attrs = match_str(cls)
            else:
                for attr in cls._tx_attrs.values():
                    arrowtail = "arrowtail=diamond, dir=both, " \
                        if attr.cont else ""
                    mult_list = attr.mult in [MULT_ZEROORMORE, MULT_ONEORMORE]
                    required = "+" if attr.mult in \
                        [MULT_ONE, MULT_ONEORMORE] else ""
                    attr_type = "list[{}]".format(attr.cls.__name__) \
                        if mult_list else attr.cls.__name__
                    if attr.ref:
                        # If attribute is a reference
                        mult = attr.mult if not attr.mult == MULT_ONE else ""
                        f.write('{} -> {}[{}headlabel="{} {}"]\n'
                                .format(id(cls), id(attr.cls), arrowtail,
                                        attr.name, mult))
                    else:
                        # If it is plain type
                        attrs += "{}{}:{}\\l".format(required,
                                                     attr.name, attr_type)

            f.write('{}[ label="{{{}|{}}}"]\n'.format(
                    id(cls), "*{}".format(name)
                    if cls._tx_type is RULE_ABSTRACT else name, attrs))

            for inherited_by in cls._tx_inh_by:
                f.write('{} -> {} [dir=back]\n'
                        .format(id(cls), id(inherited_by)))

            f.write("\n")

        f.write("\n}\n")


def model_export(model, file_name):

    processed_set = set()

    with codecs.open(file_name, 'w', encoding="utf-8") as f:
        f.write(HEADER)

        def _export(obj):

            if obj is None or obj in processed_set or type(obj) \
                    in PRIMITIVE_PYTHON_TYPES:
                return

            processed_set.add(obj)

            attrs = ""
            obj_cls = obj.__class__
            name = ""
            for attr_name, attr in obj_cls._tx_attrs.items():

                attr_value = getattr(obj, attr_name)

                endmark = 'arrowtail=diamond dir=both' if attr.cont else ""
                required = "+" if attr.mult in \
                    [MULT_ONE, MULT_ONEORMORE] else ""

                if attr.mult in [MULT_ONEORMORE, MULT_ZEROORMORE]:
                    if all([type(x) in PRIMITIVE_PYTHON_TYPES for x in attr_value]):
                        attrs += "{}{}:list=[".format(required, attr_name)
                        attrs += ",".join([str(x) for x in attr_value])
                        attrs += "]\\l"
                    else:
                        for idx, list_obj in enumerate(attr_value):
                            if list_obj is not None:
                                if type(list_obj) in PRIMITIVE_PYTHON_TYPES:
                                    f.write(
                                        '{} -> "{}:{}" [label="{}:{}" {}]\n'
                                        .format(id(obj), list_obj,
                                                type(list_obj).__name__,
                                                attr_name, idx, endmark))
                                else:
                                    f.write('{} -> {} [label="{}:{}" {}]\n'
                                            .format(id(obj), id(list_obj),
                                                    attr_name, idx, endmark))
                                    _export(list_obj)
                else:

                    # Plain attributes
                    if type(attr_value) in [str, text]:
                        attr_value = dot_escape(attr_value)

                    if type(attr_value) in PRIMITIVE_PYTHON_TYPES:
                        if attr_name == 'name':
                            name = attr_value
                        else:
                            attrs += "{}{}:{}={}\\l".format(
                                required, attr_name, type(attr_value)
                                .__name__, attr_value)
                    else:
                        # Object references
                        if attr_value is not None:
                            f.write('{} -> {} [label="{}" {}]\n'.format(
                                id(obj), id(attr_value),
                                attr_name, endmark))
                            _export(attr_value)

            name = "{}:{}".format(name, obj_cls.__name__)

            f.write('{}[label="{{{}|{}}}"]\n'.format(id(obj), name, attrs))

        _export(model)

        f.write('\n}\n')
