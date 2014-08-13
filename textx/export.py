#-*- coding: utf-8 -*-
#######################################################################
# Name: export.py
# Purpose: Export of textX based models and metamodels to dot file
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################
from itertools import chain
from textx import PRIMITIVE_TYPE_NAMES, TextXMetaClass

PRIMITIVE_PYTHON_TYPES = [int, float, str, bool]

HEADER = '''
    digraph xtext {
    fontname = "Bitstream Vera Sans"
    fontsize = 8
    node[
        shape=record,
        style=filled,
        fillcolor=gold
    ]
    edge[dir=black,arrowtail=empty]


'''

def metamodel_export(meta_model, file_name):
    processed_set = set()


    with open(file_name, 'w') as f:
        f.write(HEADER)

        for name, m in meta_model.items():
            attrs = ""
            for attr_name, attr_type in m.attrib_types.items():
                # Check if reference
                reference = False
                for ref in m.refs:
                    if ref[0] == attr_name:
                        reference = True
                        break
                for cont in m.cont:
                    if cont[0] == attr_name:
                        reference = True
                        break
                if not reference:
                    if attr_type is not None:
                        attrs += "+{}:{}\\l".format(attr_name, attr_type)
                    else:
                        attrs += "+{}\\l".format(attr_name)

            inheritance = ""
            for inherited_by in m.inh_by:
                inheritance += '{} -> {} [dir=back]\n'.format(name, inherited_by.__name__)

            containments = ""
            for cont in m.cont:
                attr_name, metacls, mult = cont
                containments += '{} -> {}[arrowtail=diamond, dir=both, headlabel="{} {}"]\n'\
                        .format(name, metacls.__name__, attr_name, '')

            references = ""
            for ref in m.refs:
                attr_name, metacls, mult = ref
                references += '{} -> {}[arrowhead=normal, headlabel="{} {}"]\n'\
                        .format(name, metacls.__name__, attr_name, mult)

            f.write('{}[ label="{{{}|{}}}"]\n'.format(\
                    name, name, attrs))
            f.write(inheritance)
            f.write(containments)
            f.write(references)
            f.write("\n")


        f.write("\n}\n")


def model_export(model, file_name):

    processed_set = set()

    with open(file_name, 'w') as f:
        f.write(HEADER)

        def _export(m):

            if m in processed_set or type(m) in PRIMITIVE_PYTHON_TYPES:
                return

            processed_set.add(m)

            attrs = ""
            obj_cls_name = m.__class__.__name__
            metaclass_info = model._metacls_info[obj_cls_name]
            refs_cont_names = [ref[0] \
                    for ref in chain(metaclass_info.refs, metaclass_info.cont)]
            ref_names = [ref[0] for ref in metaclass_info.refs]
            cont_names = [ref[0] for ref in metaclass_info.cont]
            name = ""
            for attr_name, attr_type in metaclass_info.attrib_types.items():

                value = getattr(m, attr_name)
                endmark = 'arrowtail=diamond dir=both' if attr_name in cont_names else ""

                # Plain attributes
                if type(value) in PRIMITIVE_PYTHON_TYPES:
                    if attr_name == 'name':
                        name = value
                    else:
                        attrs += "{}:{}={}\\l".format(attr_name, type(value).__name__, value)

                # Object references
                elif isinstance(value, TextXMetaClass):
                    f.write('{} -> {} [label="{}" {}]\n'.format(id(m), id(value),
                        attr_name, endmark))
                    _export(value)

                # List of references or primitive values
                elif type(value) is list:
                    if attr_name in refs_cont_names:
                        for idx, obj in enumerate(value):
                            f.write('{} -> {} [label="{}:{}" {}]\n'\
                                    .format(id(m), id(obj), attr_name, idx, endmark))
                            _export(obj)
                    else:
                        attrs += "{}:list=[".format(attr_name)
                        attrs += ",".join(value)
                        attrs += "]\\l"


            name = "{}:{}".format(name,obj_cls_name)

            f.write('{}[label="{{{}|{}}}"]\n'.format(id(m), name, attrs))

        _export(model)

        f.write('\n}\n')


