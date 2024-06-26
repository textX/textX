"""
Export of textX based models and metamodels to dot file.
"""
import codecs
from dataclasses import dataclass
from typing import List, Union
from typing import Optional as Opt

from arpeggio import (
    Match,
    OneOrMore,
    Optional,
    OrderedChoice,
    ParsingExpression,
    Sequence,
    ZeroOrMore,
)

from textx.const import (
    MULT_ONE,
    MULT_ONEORMORE,
    MULT_ZEROORMORE,
    RULE_ABSTRACT,
    RULE_COMMON,
    RULE_MATCH,
)
from textx.lang import ALL_TYPE_NAMES, BASE_TYPE_NAMES, PRIMITIVE_PYTHON_TYPES
from textx.metamodel import MetaAttr, TextXMetaClass

HEADER = """
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


"""


def dot_match_str(cls, other_match_rules=None):
    """
    For a given match rule meta-class returns a nice string representation for
    the body.
    """

    def r(s):
        # print("==>" + str(s) + " " + s.rule_name)
        if s.root and (
            s in visited
            or s.rule_name in ALL_TYPE_NAMES
            or (
                hasattr(s, "_tx_class")
                and (
                    s._tx_class._tx_type is not RULE_MATCH
                    or (s._tx_class in other_match_rules and s._tx_class is not cls)
                )
            )
        ):
            # print("==> NAME " + s.rule_name)
            return s.rule_name

        visited.add(s)
        if isinstance(s, Match):
            result = str(s)
        elif isinstance(s, OrderedChoice):
            result = "|".join([r(x) for x in s.nodes])
        elif isinstance(s, Sequence):
            result = " ".join([r(x) for x in s.nodes])
        elif isinstance(s, ZeroOrMore):
            result = f"({r(s.nodes[0])})*"
        elif isinstance(s, OneOrMore):
            result = f"({r(s.nodes[0])})+"
        elif isinstance(s, Optional):
            result = f"{r(s.nodes[0])}?"
        else:
            # breakpoint()
            # print("#### {}".format(s.__class__.__name__))
            result = "{}({})".format(
                s.__class__.__name__, ",".join([r(x) for x in s.nodes])
            )
        return "{}{}".format(result, "-" if s.suppress else "")

    mstr = ""
    # print("---------- "+str(cls))
    if not (cls.typ is RULE_ABSTRACT and cls.name != cls.peg_rule.rule_name):
        e = cls.peg_rule
        visited = set()
        if other_match_rules is None:
            other_match_rules = set()
        if not isinstance(e, Match):
            visited.add(e)
        if isinstance(e, OrderedChoice):
            mstr = "|".join(
                [r(x) for x in e.nodes if x.rule_name in BASE_TYPE_NAMES or not x.root]
            )
        elif isinstance(e, Sequence):
            mstr = " ".join([r(x) for x in e.nodes])
        else:
            mstr = r(e)

    return mstr


def dot_escape(s):
    return (
        s.replace("\n", r"\n")
        .replace("\\", "\\\\")
        .replace('"', r"\"")
        .replace("|", r"\|")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace(">", r"\>")
        .replace("<", r"\<")
        .replace("?", r"\?")
    )


def html_escape(s):
    from html import escape

    return escape(s)


def dot_repr(o):
    if isinstance(o, str):
        escaped = dot_escape(str(o))
        if len(escaped) > 20:
            return f"'{escaped[:20]}...'"
        else:
            return f"'{escaped}'"
    else:
        return str(o)


@dataclass
class Attr:
    name: str
    cls: 'Cls'
    mult: str
    cont: bool
    ref: bool
    bool_assignment: bool
    position: int


@dataclass
class Cls:
    name: str
    fqn: str
    typ: str
    attrs: List[Union[MetaAttr, Attr]]
    inh_by: List['Cls']
    inh_from: Opt['Cls']
    peg_rule: ParsingExpression

    def __hash__(self):
        return hash(self.fqn)


class Renderer:
    def __init__(self):
        self.match_rules = set()


class DotRenderer(Renderer):
    def get_header(self):
        return HEADER

    def get_match_rules_table(self):
        trailer = ""
        if self.match_rules:
            trailer = "<table>\n"
            for cls in sorted(self.match_rules, key=lambda x: x.fqn):
                trailer += "\t<tr>\n"
                attrs = dot_match_str(cls, self.match_rules)
                trailer += f"\t\t<td><b>{cls.name}</b></td>" \
                           f"<td>{html_escape(attrs)}</td>\n"
                trailer += "\t</tr>\n"
            trailer += "</table>"
        return trailer

    def get_trailer(self):
        trailer = ""
        if self.match_rules:
            trailer = f"match_rules [ shape=plaintext, " \
                      f"label=< {self.get_match_rules_table()} >]\n\n"
        return trailer + "\n}\n"

    def render_class(self, cls):
        name = cls.name
        attrs = ""
        if cls.typ is RULE_MATCH:
            if cls.name not in BASE_TYPE_NAMES:
                self.match_rules.add(cls)
            return ""
        elif cls.typ is not RULE_ABSTRACT:
            for attr in cls.attrs:
                required = attr.mult in [MULT_ONE, MULT_ONEORMORE]
                mult_list = attr.mult in [MULT_ZEROORMORE, MULT_ONEORMORE]
                attr_type = (
                    f"list[{attr.cls.name}]" if mult_list else attr.cls.name
                )
                if attr.ref and attr.cls.name != "OBJECT":
                    pass
                else:
                    # If it is plain type
                    attrs += "{}: {}\\l".format(
                        attr.name,
                        attr_type if required else rf"optional\<{attr_type}\>",
                    )
        return '{}[ label="{{{}|{}}}"]\n\n'.format(
            id(cls), f"*{name}" if cls.typ is RULE_ABSTRACT else name, attrs
        )

    def render_attr_link(self, cls, attr):
        arrowtail = "arrowtail=diamond, dir=both, " if attr.cont else ""
        if attr.ref and attr.cls.name != "OBJECT":
            # If attribute is a reference
            mult = attr.mult if attr.mult != MULT_ONE else ""
            return f'{id(cls)} -> ' \
                f'{id(attr.cls)}[{arrowtail}headlabel="{attr.name} {mult}"]\n'

    def render_inherited_by(self, base, special):
        return f"{id(base)} -> {id(special)} [dir=back]\n"


class PlantUmlRenderer(Renderer):
    def __init__(self, linetype=None):
        self.linetype = linetype
        super().__init__()

    def get_header(self):
        return """@startuml
set namespaceSeparator .
{}
""".format(f"skinparam linetype {self.linetype}"
           if self.linetype else "")

    def get_trailer(self):
        trailer = ""
        if self.match_rules:
            trailer += "\nlegend\n"
            trailer += "  Match rules:\n"
            trailer += "  |= Name  |= Rule details |\n"
            for cls in self.match_rules:
                # print("-*-> " + cls.__name__)
                trailer += "  | {} | {} |\n".format(  # noqa
                    cls.name,
                    dot_escape(dot_match_str(cls, self.match_rules)),  # reuse
                )
            trailer += "end legend\n\n"
        trailer += "@enduml\n"
        return trailer

    def render_class(self, cls):
        attrs = ""
        stereotype = ""
        if cls.typ is RULE_MATCH:
            if cls.name not in BASE_TYPE_NAMES:
                self.match_rules.add(cls)
            return ""
        elif cls.typ is not RULE_COMMON:
            stereotype += cls.typ
        else:
            for attr in cls.attrs:
                required = attr.mult in [MULT_ONE, MULT_ONEORMORE]
                mult_list = attr.mult in [MULT_ZEROORMORE, MULT_ONEORMORE]
                attr_type = (
                    f"list[{attr.cls.name}]" if mult_list else attr.cls.name
                )
                if attr.ref and attr.cls.name != "OBJECT":
                    pass
                else:
                    if required:
                        attrs += f"  {attr.name} : {attr_type}\n"
                    else:
                        attrs += f"  {attr.name} : optional<{attr_type}>\n"
        if len(stereotype) > 0:
            stereotype = "<<" + stereotype + ">>"
        return f"\n\nclass {cls.fqn} {stereotype} {{\n{attrs}}}\n"

    def render_attr_link(self, cls, attr):
        if attr.ref and attr.cls.name != "OBJECT":
            # If attribute is a reference
            # mult = attr.mult if not attr.mult == MULT_ONE else ""
            arr = "*-->" if attr.cont else "-->"
            name = attr.name
            mult = f'"{attr.mult}"' if attr.mult != "1" else ""
            return f'{cls.fqn} {arr} {mult} {attr.cls.fqn}: {name}\n'

    def render_inherited_by(self, base, special):
        return f"{base.fqn} <|-- {special.fqn}\n"


def metamodel_export(metamodel, file_name, renderer=None):
    with codecs.open(file_name, "w", encoding="utf-8") as f:
        metamodel_export_tofile(metamodel, f, renderer)


def metamodel_export_tofile(metamodel, f, renderer=None):
    if renderer is None:
        renderer = DotRenderer()
    f.write(renderer.get_header())
    classes = get_unified_classes(metamodel)
    classes = [c for c in classes if c.fqn not in ALL_TYPE_NAMES]
    for cls in classes:
        if cls.name not in ALL_TYPE_NAMES:
            f.write(renderer.render_class(cls))
    f.write("\n\n")
    for cls in classes:
        for attr in cls.attrs:
            if attr.ref and attr.cls.name != "OBJECT":
                f.write(renderer.render_attr_link(cls, attr))
            if attr.cls not in classes:
                f.write(renderer.render_class(attr.cls))
        for inherited_by in cls.inh_by:
            f.write(renderer.render_inherited_by(cls, inherited_by))
    f.write(f"{renderer.get_trailer()}")


def get_unified_classes(classes: List[TextXMetaClass]) -> List[Cls]:
    """
    Create list of Cls which is used for attribute/links unification
    respecting the inheritance hierarchy chain.
    See https://github.com/textX/textX/issues/423
    """
    new_classes = dict()
    for cls in classes:
        c = Cls(cls.__name__, cls._tx_fqn, cls._tx_type,
                cls._tx_attrs.values(), cls._tx_inh_by, None,
                cls._tx_peg_rule)
        new_classes[cls._tx_fqn] = c

    # resolve attributes
    for new_cls in new_classes.values():
        # HACK: `if` in this comprehension is is a temporary fix for
        #       test_import.py tests. Apparently, relative.fourth.Second is not
        #       part of the meta-model but it should be.
        new_cls.attrs = [Attr(attr.name, new_classes[attr.cls._tx_fqn],
                            attr.mult, attr.cont, attr.ref,
                            attr.bool_assignment, attr.position)
                         for attr in new_cls.attrs
                         if attr.cls._tx_fqn in new_classes]

    # resolve inheritance
    for new_cls in new_classes.values():
        new_cls.inh_by = [new_classes[inh._tx_fqn] for inh in new_cls.inh_by]
        if new_cls.inh_from:
            new_cls.inh_from = new_classes[new_cls.inh_from._tx_fqn]

    # Raise attributes
    change = True
    while change:
        change = False
        for new_cls in new_classes.values():
            # If there are same attributes in all inherited classes
            # raise them to current class
            if new_cls.inh_by:
                first = new_cls.inh_by[0]
                for attr in first.attrs:
                    for other in new_cls.inh_by[1:]:
                        if attr not in other.attrs:
                            break
                    else:
                        # Attribute found in all inherited classes
                        # Move it up
                        if attr.name not in [attr.name
                                             for attr in new_cls.attrs]:
                            new_cls.attrs.append(attr)
                        for inh in new_cls.inh_by:
                            inh.attrs.remove(attr)
                        change = True

    return new_classes.values()



def model_export(model, file_name, repo=None):
    """
    Args:
        model: the model to be exported (may be None if repo is not None)
        file_name: the output file name
        repo: the model repo (alternative to model input) to be exported

    Returns:
        Nothing
    """
    with codecs.open(file_name, "w", encoding="utf-8") as f:
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
        raise Exception("specify either a model or a repo")
    if model and repo:
        raise Exception("specify either a model or a repo")

    processed_set = set()
    f.write(HEADER)

    def _export(obj):
        if obj is None or id(obj) in processed_set or type(obj) in PRIMITIVE_PYTHON_TYPES:
            return

        processed_set.add(id(obj))

        attrs = ""
        obj_cls = obj.__class__
        name = ""
        if hasattr(obj_cls, "_tx_attrs"):
            for attr_name, attr in obj_cls._tx_attrs.items():
                attr_value = getattr(obj, attr_name)
                if attr_value is None:
                    continue

                endmark = "arrowtail=diamond dir=both" if attr.cont else ""
                required = "+" if attr.mult in [MULT_ONE, MULT_ONEORMORE] else ""

                if attr.mult in [MULT_ONEORMORE, MULT_ZEROORMORE]:
                    if all([type(x) in PRIMITIVE_PYTHON_TYPES for x in attr_value]):
                        attrs += f"{required}{attr_name}:list=["
                        attrs += ",".join([dot_repr(x) for x in attr_value])
                        attrs += "]\\l"
                    else:
                        for idx, list_obj in enumerate(attr_value):
                            if list_obj is not None:
                                if type(list_obj) in PRIMITIVE_PYTHON_TYPES:
                                    f.write(
                                        f'{id(obj)} -> "{list_obj}:{type(list_obj).__name__}"'  # noqa
                                        f' [label="{attr_name}:{idx}" {endmark}]\n'
                                    )
                                else:
                                    f.write(
                                        f'{id(obj)} -> {id(list_obj)} '
                                        f'[label="{attr_name}:{idx}" {endmark}]\n'
                                    )
                                    _export(list_obj)
                else:
                    # Plain attributes
                    if isinstance(attr_value, str) and attr_name != "name":
                        attr_value = dot_repr(attr_value)

                    if type(attr_value) in PRIMITIVE_PYTHON_TYPES:
                        if attr_name == "name":
                            name = attr_value
                        else:
                            attrs += f"{required}{attr_name}:" \
                                     f"{type(attr_value).__name__}={attr_value}\\l"
                    else:
                        # Object references
                        if attr_value is not None:
                            f.write(
                                f'{id(obj)} -> {id(attr_value)} '
                                f'[label="{attr_name}" {endmark}]\n'
                            )
                            _export(attr_value)

        name = f"{name}:{obj_cls.__name__}"

        f.write(f'{id(obj)}[label="{{{name}|{attrs}}}"]\n')

    def _export_subgraph(m):
        from textx import get_children

        f.write(f'subgraph "cluster_{m._tx_filename}" {{\n')
        f.write(
            f"""
        penwidth=2.0
        color=darkorange4;
        label = "{m._tx_filename}";
                    """
        )
        for obj in get_children(lambda _: True, m):
            f.write(f"{id(obj)};\n")
        f.write("\n}\n")

    if repo or hasattr(model, "_tx_model_repository"):
        if not repo:
            repo = model._tx_model_repository.all_models
            if not repo:
                _export(model)
        for m in repo:
            _export_subgraph(m)
            _export(m)
    else:
        _export(model)

    f.write("\n}\n")
