# -*- coding: utf-8 -*-
#######################################################################
# Name: export.py
# Purpose: Export of textX based models and metamodels to dot file
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################
from __future__ import unicode_literals
import codecs
import sys
if sys.version < '3':
    text = unicode
else:
    text = str

from .const import MULT_ZEROORMORE, MULT_ONEORMORE, MULT_ONE, RULE_MATCH
from .textx import BASE_TYPE_NAMES

PRIMITIVE_PYTHON_TYPES = [int, float, str, bool]

HEADER = '''
    digraph xtext {
    fontname = "Bitstream Vera Sans"
    fontsize = 8
    node[
        shape=record,
        style=filled,
        fillcolor=aliceblue
    ]
    edge[dir=black,arrowtail=empty]


'''


def metamodel_export(metamodel, file_name):

    with codecs.open(file_name, 'w', encoding="utf-8") as f:
        f.write(HEADER)

        for cls in metamodel:
            name = cls.__name__
            attrs = ""
            if cls._type == RULE_MATCH:
                attrs = cls._match_str.replace("|", "\\|")\
                                      .replace('"', '\\"')\
                                      .replace('{', '\\{')\
                                      .replace('}', '\\}')
            else:
                for attr in cls._attrs.values():
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
                    id(cls), name, attrs))

            for inherited_by in cls._inh_by:
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
            for attr_name, attr in obj_cls._attrs.items():

                attr_value = getattr(obj, attr_name)

                endmark = 'arrowtail=diamond dir=both' if attr.cont else ""
                required = "+" if attr.mult in \
                    [MULT_ONE, MULT_ONEORMORE] else ""

                if attr.mult in [MULT_ONEORMORE, MULT_ZEROORMORE]:
                    if not attr.ref:
                        attrs += "{}{}:list=[".format(required, attr_name)
                        attrs += ",".join([str(x) for x in attr_value])
                        attrs += "]\\l"
                    else:
                        for idx, list_obj in enumerate(attr_value):
                            if list_obj is not None:
                                f.write('{} -> {} [label="{}:{}" {}]\n'
                                        .format(id(obj), id(list_obj),
                                                attr_name, idx, endmark))
                                _export(list_obj)
                else:
                    # Plain attributes
                    if not attr.ref:
                        if attr_name == 'name':
                            name = attr_value
                        else:
                            if attr.cls.__name__ in BASE_TYPE_NAMES \
                                    or attr.cls._type == RULE_MATCH:
                                if type(attr_value) in [str, text]:
                                    attr_value = \
                                        attr_value.replace('\n', r'\n')\
                                        .replace('"', '\\"')
                                attrs += "{}{}:{}={}\\l".format(
                                    required, attr_name, type(attr_value)
                                    .__name__, attr_value)
                            else:
                                attrs += "{}{}:{}\\l".format(
                                    required, attr_name, type(attr_value)
                                    .__name__)
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
