"""
Export of textX based models and metamodels to dot file.
"""
import codecs

from arpeggio import Match, OneOrMore, Optional, OrderedChoice, Sequence, ZeroOrMore

from textx.const import (
    MULT_ONE,
    MULT_ONEORMORE,
    MULT_ZEROORMORE,
    RULE_ABSTRACT,
    RULE_COMMON,
    RULE_MATCH,
)
from textx.lang import ALL_TYPE_NAMES, BASE_TYPE_NAMES, PRIMITIVE_PYTHON_TYPES

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
    if not (cls._tx_type is RULE_ABSTRACT and cls.__name__ != cls._tx_peg_rule.rule_name):
        e = cls._tx_peg_rule
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


class DotRenderer:
    def __init__(self):
        self.match_rules = set()

    def get_header(self):
        return HEADER

    def get_match_rules_table(self):
        trailer = ""
        if self.match_rules:
            trailer = "<table>\n"
            for cls in sorted(self.match_rules, key=lambda x: x._tx_fqn):
                trailer += "\t<tr>\n"
                attrs = dot_match_str(cls, self.match_rules)
                trailer += "\t\t<td><b>{}</b></td><td>{}</td>\n".format(
                    cls.__name__, html_escape(attrs)
                )
                trailer += "\t</tr>\n"
            trailer += "</table>"
        return trailer

    def get_trailer(self):
        trailer = ""
        if self.match_rules:
            trailer = "match_rules [ shape=plaintext, label=< {} >]\n\n".format(
                self.get_match_rules_table()
            )
        return trailer + "\n}\n"

    def render_class(self, cls):
        name = cls.__name__
        attrs = ""
        if cls._tx_type is RULE_MATCH:
            if cls.__name__ not in BASE_TYPE_NAMES:
                self.match_rules.add(cls)
            return ""
        elif cls._tx_type is not RULE_ABSTRACT:
            for attr in cls._tx_attrs.values():
                required = attr.mult in [MULT_ONE, MULT_ONEORMORE]
                mult_list = attr.mult in [MULT_ZEROORMORE, MULT_ONEORMORE]
                attr_type = (
                    f"list[{attr.cls.__name__}]" if mult_list else attr.cls.__name__
                )
                if attr.ref and attr.cls.__name__ != "OBJECT":
                    pass
                else:
                    # If it is plain type
                    attrs += "{}: {}\\l".format(
                        attr.name,
                        attr_type if required else rf"optional\<{attr_type}\>",
                    )
        return '{}[ label="{{{}|{}}}"]\n\n'.format(
            id(cls), f"*{name}" if cls._tx_type is RULE_ABSTRACT else name, attrs
        )

    def render_attr_link(self, cls, attr):
        arrowtail = "arrowtail=diamond, dir=both, " if attr.cont else ""
        if attr.ref and attr.cls.__name__ != "OBJECT":
            # If attribute is a reference
            mult = attr.mult if attr.mult != MULT_ONE else ""
            return '{} -> {}[{}headlabel="{} {}"]\n'.format(
                id(cls), id(attr.cls), arrowtail, attr.name, mult
            )

    def render_inherited_by(self, base, special):
        return f"{id(base)} -> {id(special)} [dir=back]\n"


class PlantUmlRenderer:
    def __init__(self):
        self.match_rules = set()

    def get_header(self):
        return """@startuml
set namespaceSeparator .
"""

    def get_trailer(self):
        trailer = ""
        if self.match_rules:
            trailer += "\nlegend\n"
            trailer += "  Match rules:\n"
            trailer += "  |= Name  |= Rule details |\n"
            for cls in self.match_rules:
                # print("-*-> " + cls.__name__)
                trailer += "  | {} | {} |\n".format(
                    cls.__name__,
                    dot_escape(dot_match_str(cls, self.match_rules)),  # reuse
                )
            trailer += "end legend\n\n"
        trailer += "@enduml\n"
        return trailer

    def render_class(self, cls):
        attrs = ""
        stereotype = ""
        if cls._tx_type is RULE_MATCH:
            if cls.__name__ not in BASE_TYPE_NAMES:
                self.match_rules.add(cls)
            return ""
        elif cls._tx_type is not RULE_COMMON:
            stereotype += cls._tx_type
        else:
            for attr in cls._tx_attrs.values():
                required = attr.mult in [MULT_ONE, MULT_ONEORMORE]
                mult_list = attr.mult in [MULT_ZEROORMORE, MULT_ONEORMORE]
                attr_type = (
                    f"list[{attr.cls.__name__}]" if mult_list else attr.cls.__name__
                )
                if attr.ref and attr.cls.__name__ != "OBJECT":
                    pass
                else:
                    if required:
                        attrs += f"  {attr.name} : {attr_type}\n"
                    else:
                        attrs += f"  {attr.name} : optional<{attr_type}>\n"
        if len(stereotype) > 0:
            stereotype = "<<" + stereotype + ">>"
        return f"\n\nclass {cls._tx_fqn} {stereotype} {{\n{attrs}}}\n"

    def render_attr_link(self, cls, attr):
        if attr.ref and attr.cls.__name__ != "OBJECT":
            # If attribute is a reference
            # mult = attr.mult if not attr.mult == MULT_ONE else ""
            arr = "*-->" if attr.cont else "o-->"
            name = attr.name
            if attr.mult != "1":
                name += " " + attr.mult
            return f"{cls._tx_fqn} {arr} {attr.cls._tx_fqn}: {name}\n"

    def render_inherited_by(self, base, special):
        return f"{base._tx_fqn} <|-- {special._tx_fqn}\n"


def metamodel_export(metamodel, file_name, renderer=None):
    with codecs.open(file_name, "w", encoding="utf-8") as f:
        metamodel_export_tofile(metamodel, f, renderer)


def metamodel_export_tofile(metamodel, f, renderer=None):
    if renderer is None:
        renderer = DotRenderer()
    f.write(renderer.get_header())
    classes = [c for c in metamodel if c._tx_fqn not in ALL_TYPE_NAMES]
    for cls in classes:
        f.write(renderer.render_class(cls))
    f.write("\n\n")
    for cls in classes:
        if cls._tx_type is not RULE_COMMON:
            pass
        else:
            for attr in cls._tx_attrs.values():
                if attr.ref and attr.cls.__name__ != "OBJECT":
                    f.write(renderer.render_attr_link(cls, attr))
                if attr.cls not in classes:
                    f.write(renderer.render_class(attr.cls))
        for inherited_by in cls._tx_inh_by:
            f.write(renderer.render_inherited_by(cls, inherited_by))
    f.write(f"{renderer.get_trailer()}")


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
        raise Exception("specity either a model or a repo")
    if model and repo:
        raise Exception("specity either a model or a repo")

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
                                        '{} -> "{}:{}" [label="{}:{}" {}]\n'.format(
                                            id(obj),
                                            list_obj,
                                            type(list_obj).__name__,
                                            attr_name,
                                            idx,
                                            endmark,
                                        )
                                    )
                                else:
                                    f.write(
                                        '{} -> {} [label="{}:{}" {}]\n'.format(
                                            id(obj), id(list_obj), attr_name, idx, endmark
                                        )
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
                            attrs += "{}{}:{}={}\\l".format(
                                required, attr_name, type(attr_value).__name__, attr_value
                            )
                    else:
                        # Object references
                        if attr_value is not None:
                            f.write(
                                '{} -> {} [label="{}" {}]\n'.format(
                                    id(obj), id(attr_value), attr_name, endmark
                                )
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
