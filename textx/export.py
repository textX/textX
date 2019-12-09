# -*- coding: utf-8 -*-
"""
Export of textX based models and metamodels to dot file.
"""
from __future__ import unicode_literals
from arpeggio import Match, OrderedChoice, Sequence, OneOrMore, ZeroOrMore,\
    Optional, SyntaxPredicate
from textx.const import MULT_ZEROORMORE, MULT_ONEORMORE, MULT_ONE, \
    RULE_ABSTRACT, RULE_COMMON, RULE_MATCH
from textx.lang import PRIMITIVE_PYTHON_TYPES, BASE_TYPE_NAMES, ALL_TYPE_NAMES
import codecs
import sys
if sys.version < '3':
    text = unicode  # noqa
else:
    text = str


HEADER = '''
    digraph textX {
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


def match_abstract_str(cls):
    """
    For a given abstract or match rule meta-class returns a nice string
    representation for the body.
    """
    def r(s):
        if s.root:
            if s in visited or s.rule_name in ALL_TYPE_NAMES or \
                    (hasattr(s, '_tx_class') and
                     s._tx_class._tx_type is not RULE_MATCH):
                return s.rule_name

        visited.add(s)
        if isinstance(s, Match):
            result = text(s)
        elif isinstance(s, OrderedChoice):
            result = "|".join([r(x) for x in s.nodes])
        elif isinstance(s, Sequence):
            result = " ".join([r(x) for x in s.nodes])
        elif isinstance(s, ZeroOrMore):
            result = "({})*".format(r(s.nodes[0]))
        elif isinstance(s, OneOrMore):
            result = "({})+".format(r(s.nodes[0]))
        elif isinstance(s, Optional):
            result = "{}?".format(r(s.nodes[0]))
        elif isinstance(s, SyntaxPredicate):
            result = ""
        return "{}{}".format(result, "-" if s.suppress else "")

    mstr = ""
    if cls.__name__ not in ALL_TYPE_NAMES and \
            not (cls._tx_type is RULE_ABSTRACT and
                 cls.__name__ != cls._tx_peg_rule.rule_name):
        e = cls._tx_peg_rule
        visited = set()
        if not isinstance(e, Match):
            visited.add(e)
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
            .replace('>', r'\>')\
            .replace('<', r'\<')\
            .replace('?', r'\?')


def dot_repr(o):
    if type(o) is text:
        return "'{}'".format(dot_escape(text(o)))
    else:
        return text(o)


class DotRenderer(object):

    def get_header(self):
        return HEADER

    def get_trailer(self):
        return '\n}\n'

    def render_class(self, cls):
        name = cls.__name__
        attrs = ""
        if cls._tx_type is not RULE_COMMON:
            attrs = match_abstract_str(cls)
        else:
            for attr in cls._tx_attrs.values():
                required = attr.mult in [MULT_ONE, MULT_ONEORMORE]
                mult_list = attr.mult in [MULT_ZEROORMORE, MULT_ONEORMORE]
                attr_type = "list[{}]".format(attr.cls.__name__) \
                    if mult_list else attr.cls.__name__
                if attr.ref and attr.cls.__name__ != 'OBJECT':
                    pass
                else:
                    # If it is plain type
                    attrs += "{}: {}\\l".format(
                        attr.name, attr_type if required else "optional\<{}\>".format(attr_type))
        return '{}[ label="{{{}|{}}}"]\n\n'.format(
                id(cls), "*{}".format(name)
                if cls._tx_type is RULE_ABSTRACT else name, attrs)

    def render_attr_link(self, cls, attr):
        arrowtail = "arrowtail=diamond, dir=both, " \
            if attr.cont else ""
        if attr.ref and attr.cls.__name__ != 'OBJECT':
            # If attribute is a reference
            mult = attr.mult if not attr.mult == MULT_ONE else ""
            return '{} -> {}[{}headlabel="{} {}"]\n'\
                .format(id(cls), id(attr.cls), arrowtail,
                        attr.name, mult)

    def render_inherited_by(self, base, special):
        return '{} -> {} [dir=back]\n'\
            .format(id(base), id(special))


class PlantUmlRenderer(object):

    def get_header(self):
        return '''@startuml
set namespaceSeparator .
'''

    def get_trailer(self):
        return '@enduml\n'

    def render_class(self, cls):
        attrs = ""
        stereotype = ""
        if cls._tx_type is not RULE_COMMON:
            stereotype += cls._tx_type
        else:
            for attr in cls._tx_attrs.values():
                required = attr.mult in [MULT_ONE, MULT_ONEORMORE]
                mult_list = attr.mult in [MULT_ZEROORMORE, MULT_ONEORMORE]
                attr_type = "list[{}]".format(attr.cls.__name__) \
                    if mult_list else attr.cls.__name__
                if attr.ref and attr.cls.__name__ != 'OBJECT':
                    pass
                else:
                    if required:
                        attrs += "  {} {}\n".format(attr_type, attr.name)
                    else:
                        attrs += "  optional<{}> {}\n".format(attr_type,
                                                              attr.name)
        if len(stereotype) > 0:
            stereotype = "<<"+stereotype+">>"
        return '\n\nclass {} {} {{\n{}}}\n'.format(
                cls._tx_fqn, stereotype, attrs
                )

    def render_attr_link(self, cls, attr):
        if attr.ref and attr.cls.__name__ != 'OBJECT':
            # If attribute is a reference
            # mult = attr.mult if not attr.mult == MULT_ONE else ""
            if attr.cont:
                arr = "*--"
            else:
                arr = "o--"
            if attr.mult == MULT_ZEROORMORE:
                arr = arr + ' "0..*"'
            elif attr.mult == MULT_ONEORMORE:
                arr = arr + ' "1..*"'
            return '{} {} {}\n'.format(
                cls._tx_fqn, arr, attr.cls._tx_fqn)

    def render_inherited_by(self, base, special):
        return '{} <|-- {}\n'.format(base._tx_fqn, special._tx_fqn)


def metamodel_export(metamodel, file_name, renderer=None):
    with codecs.open(file_name, 'w', encoding="utf-8") as f:
        metamodel_export_tofile(metamodel, f, renderer)


def metamodel_export_tofile(metamodel, f, renderer=None):
    if renderer is None:
        renderer = DotRenderer()
    f.write(renderer.get_header())
    for cls in metamodel:
        f.write(renderer.render_class(cls))
    f.write("\n\n")
    for cls in metamodel:
        if cls._tx_type is not RULE_COMMON:
            pass
        else:
            for attr in cls._tx_attrs.values():
                if attr.ref and attr.cls.__name__ != 'OBJECT':
                    f.write(renderer.render_attr_link(cls, attr))
        for inherited_by in cls._tx_inh_by:
            f.write(renderer.render_inherited_by(cls, inherited_by))
    f.write("{}".format(renderer.get_trailer()))


def model_export(model, file_name, repo=None):
    """
    Args:
        model: the model to be exported (may be None if repo is not None)
        file_name: the output file name
        repo: the model repo (alternative to model input) to be exported

    Returns:
        Nothing
    """
    with codecs.open(file_name, 'w', encoding="utf-8") as f:
        model_export_to_file(f, model, repo)


def model_export_to_file(f, model=None, repo=None):
    """
    Args:
        f: the file object to be used as output.
        model: the model to be exported (alternative to repo)
        repo: the repo to be exported (alternative to model)

    Returns:
        Nothing
    """
    if not model and not repo:
        raise Exception("specity either a model or a repo")
    if model and repo:
        raise Exception("specity either a model or a repo")

    processed_set = set()
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
                if all([type(x) in PRIMITIVE_PYTHON_TYPES
                        for x in attr_value]):
                    attrs += "{}{}:list=[".format(required, attr_name)
                    attrs += ",".join([dot_repr(x) for x in attr_value])
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
                if type(attr_value) is text and attr_name != 'name':
                    attr_value = dot_repr(attr_value)

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

    def _export_subgraph(m):
        from textx import get_children
        f.write('subgraph "cluster_{}" {{\n'.format(m._tx_filename))
        f.write('''
        penwidth=2.0
        color=darkorange4;
        label = "{}";
                    '''.format(m._tx_filename))
        for obj in get_children(lambda _: True, m):
            f.write('{};\n'.format(id(obj)))
        f.write('\n}\n')

    if repo or hasattr(model, "_tx_model_repository"):
        if not repo:
            repo = model._tx_model_repository.all_models
        for m in repo.filename_to_model.values():
            _export_subgraph(m)
            _export(m)
    else:
        _export(model)

    f.write('\n}\n')
