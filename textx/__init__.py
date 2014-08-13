#######################################################################
# Name: textx.py
# Purpose: Implementation of textX language in Arpeggio.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# The idea for this language is shamelessly stolen from the Xtext language
# but there are some subtle differences in both syntax and semantics.
# To make things clear I have named this language textX ;)
#######################################################################

from collections import namedtuple
from itertools import chain

from arpeggio import StrMatch, Optional, ZeroOrMore, OneOrMore, Sequence,\
    OrderedChoice, RegExMatch, Match, NoMatch, EOF,\
    SemanticAction,ParserPython, Combine, SemanticActionSingleChild,\
    SemanticActionBodyWithBraces, Terminal, ParsingExpression
from arpeggio.export import PMDOTExporter, PTDOTExporter
from arpeggio import RegExMatch as _

from textx.parser import get_language_parser


# textX grammar
def textx_model():          return ZeroOrMore(rule), EOF
def rule():                 return [metaclass, enum]
def enum():                 return enum_kwd, ident, ':', enum_literal,\
                                    ZeroOrMore("|", enum_literal), ';'
def enum_literal():         return ident, '=', str_match
def metaclass():            return metaclass_name, ":", [alternative_inher,
                                                alternative_match, sequence], ';'
def metaclass_name():       return ident

def alternative_inher():    return rule_match_alt, OneOrMore("|", rule_match_alt)
def alternative_match():    return [terminal_match, rule_match_alt], OneOrMore("|",
                                    [terminal_match, rule_match_alt])
def rule_match_alt():       return ident
def choice():               return sequence, ZeroOrMore("|", sequence)
def sequence():             return OneOrMore([assignment, expr])

def expr():                 return [terminal_match, bracketed_choice],\
                                    Optional(repeat_operator)
def bracketed_choice():     return '(', choice, ')'
def repeat_operator():      return ['*', '?', '+']

# Assignment
def assignment():           return attribute, assignment_op, assignment_rhs
def attribute():            return ident
def assignment_op():        return ["=", "*=", "+=", "?="]
def assignment_rhs():       return [terminal_match, list_match, rule_ref]
def terminal_match():       return [str_match, re_match]
def str_match():            return [("'", _(r"((\\')|[^'])*"),"'"),\
                                    ('"', _(r'((\\")|[^"])*'),'"')]
def re_match():             return "/", _(r"((\\/)|[^/])*"), "/"
def list_match():           return "{", rule_ref, Optional(list_separator), '}'
def list_separator():       return terminal_match
# Rule reference
def rule_ref():             return [rule_match, rule_link]
def rule_match():           return ident
def rule_link():            return '[', rule_name, Optional('|', rule_rule), ']'
#def rule_choice():          return rule_name, ZeroOrMore('|', rule_name)
def rule_name():            return ident
def rule_rule():            return ident

def ident():                return _(r'\w+')
def enum_kwd():             return 'enum'

# Comments
def comment():              return [comment_line, comment_block]
def comment_line():         return _(r'//.*$')
def comment_block():        return _(r'/\*(.|\n)*?\*/')


# Special rules - primitive types
ID      = _(r'[^\d\W]\w*\b', rule_name='ID', root=True)
BOOL    = _(r'true|false|0|1', rule_name='BOOL', root=True)
INT     = _(r'[-+]?[0-9]+', rule_name='INT', root=True)
FLOAT   = _(r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?', 'FLOAT', root=True)
STRING  = _(r'("[^"]*")|(\'[^\']*\')', 'STRING', root=True)
PRIMITIVE_TYPES = [ID, BOOL, INT, FLOAT, STRING]
PRIMITIVE_TYPE_NAMES = [x.rule_name for x in PRIMITIVE_TYPES]


# Str formatting functions
def str_indent(obj, indent=0, doind=False):
    """Used for metaclass instances pretty-printing."""
    if type(obj) in [str, bool, float, int]:
        if doind:
            s = get_indented(indent, str(obj))
        else:
            s = str(obj)
    elif type(obj) is list:
        s = "[\n"
        for list_value in obj:
            s += str_indent(list_value, indent+1, True)
        s += get_indented(indent, "]", newline=False)
    else:
        if hasattr(obj, 'name'):
            meta_name = '{}:{}'.format(obj.name, obj.__class__.__name__)
        else:
            meta_name = obj.__class__.__name__
        s = get_indented(indent, meta_name)

        if obj is not None:
            for attr in obj.__dict__:
                if not attr.startswith('_'):
                    # Name for each attribute
                    s += get_indented(indent + 1, "{} = {}"\
                            .format(attr, str_indent(getattr(obj, attr),
                                    indent+1, False)))
        s += '\n'
    return s

def get_indented(indent, _str, newline=True):
    indent = '\t' * indent
    return '{}{}{}'.format(indent, str(_str), '\n' if newline else '')


class RuleCrossRef(object):
    """
    Used for cross reference resolving.

    Attributes:
        rule_name(str): A name of the PEG rule that should be used to match this cross-ref.
        metaclass(str or MetaClassCrossRef): Target meta-class which is matched by
            rule_name or which name is matched by rule_name.
        position(int): A position in the input string of this cross-ref.
    """
    def __init__(self, rule_name, metaclass, position):
        self.rule_name = rule_name
        self.metaclass = metaclass
        self.position = position


class MetaClassCrossRef(object):
    """
    Helper class used for meta-class reference resolving on the meta-model level.

    Attributes:
        metacls_name(str): A name of the target metaclass.
        attr_name(str): The name of the attribute used for cross-referencing.
        position(int): The position in the input string of this cross-ref.
    """
    def __init__(self, metacls_name, attr_name, position):
        self.metacls_name= metacls_name
        self.attr_name = attr_name
        self.position = position


# attrib_types = {"attr_name": python type}
# refs = [ (attrname, metacls, mult='*'|'1'|'0..1'),... ]
# cont = [ (attrname, metacls, mult='1'|'0..1'),... ]
# inh_by = [ metacls, metacls, ...]
MetaClassInfo = namedtuple('MetaClassInfo', ['metacls', 'attrib_types',
                            'refs', 'cont', 'inh_by'])


class TextXMetaClass(object):
    """Base class for all metaclasses."""
    pass


# TextX semantic actions
class TextXModelSA(SemanticAction):
    def first_pass(self, parser, node, children):
        comments_model = parser._peg_rules.get('__comment', None)
        textx_parser = get_language_parser(children[0], comments_model,
                parser.debug)

        textx_parser._metacls_info = parser._metacls_info
        textx_parser._peg_rules = parser._peg_rules

        return textx_parser

    def _resolve_rule_refs(self, parser, textx_parser):
        """Resolves parser ParsingExpression crossrefs."""

        resolved_set = set()

        def resolve(node):
            """Recursively resolve peg rule references."""

            def _inner_resolve(rule):
                if parser.debug:
                    print("Resolving rule: {}".format(rule))

                if type(rule) == RuleCrossRef:
                    rule_name = rule.rule_name
                    if rule_name in textx_parser._peg_rules:
                        rule = textx_parser._peg_rules[rule_name]
                    else:
                        raise TextXSemanticError('Unexisting rule "{}" at position {}.'\
                                .format(rule.rule_name,
                                    parser.pos_to_linecol(rule.position)))

                assert isinstance(rule, ParsingExpression),\
                            "{}:{}".format(type(rule), str(rule))
                # Recurse
                for idx, child in enumerate(rule.nodes):
                    if not child in resolved_set:
                        resolved_set.add(rule)
                        rule.nodes[idx] = _inner_resolve(child)

                return rule

            resolved_set.add(node)
            _inner_resolve(node)

        if parser.debug:
            print("CROSS-REFS RESOLVING")

        resolve(textx_parser.parser_model)

    def _resolve_metacls_refs(self, parser, xtext_parser):

        if parser.debug:
            print("RESOLVING METACLASS REFS")

        for metacls_info in xtext_parser._metacls_info.values():

            # Inheritance
            ref_list = metacls_info.inh_by
            for idx, ref in enumerate(ref_list):
                # Must exist in metacls_info dict because we
                # have alredy checked that in _resolve_rule_refs
                ref_list[idx] = xtext_parser._metacls_info[ref.metacls_name].metacls

            # References
            ref_list = metacls_info.refs
            for idx, ref in enumerate(ref_list):
                ref_list[idx] = (ref[0],
                        xtext_parser._metacls_info[ref[1].metacls_name].metacls,
                        ref[2])

            # Containment
            ref_list = metacls_info.cont
            for idx, ref in enumerate(ref_list):
                ref_list[idx] = (ref[0],
                        xtext_parser._metacls_info[ref[1].metacls_name].metacls,
                        ref[2])

    def second_pass(self, parser, textx_parser):
        """Cross reference resolving for parser model."""

        if parser.debug:
            print("RESOLVING XTEXT PARSER: second_pass")

        self._resolve_rule_refs(parser, textx_parser)
        self._resolve_metacls_refs(parser, textx_parser)

        return textx_parser
textx_model.sem = TextXModelSA()


def metaclass_SA(parser, node, children):
    rule_name, rule = children
    rule = Sequence(nodes=[rule], rule_name=rule_name,
             root=True)

    # Do some name mangling for comment rule
    # to prevent refererencing from other rules
    if rule_name.lower() == "comment":
        rule_name = "__comment"

    parser._peg_rules[rule_name] = rule
    return rule
metaclass.sem = metaclass_SA

def metaclass_name_SA(parser, node, children):

    class Meta(TextXMetaClass):
        """
        Dynamic metaclass. Each textX rule will result in creating
        one Meta class with the type name of the rule.
        Model is a graph of python instances of this metaclasses.
        """
        def __str__(self):
            return str_indent(self)

    # Create metaclass and metacls_info record
    metacls_name = str(node)
    metacls = Meta
    metacls.__name__ = metacls_name
    metacls_info = parser._metacls_info.setdefault(metacls_name,\
            MetaClassInfo(metacls=metacls, attrib_types = {},
                refs=[], cont=[], inh_by=[]))

    parser._current_metacls_info = metacls_info

    if parser.debug:
        print("Creating metaclass: {}".format(metacls_name))

    # First rule will be the root of the meta-model
    if not parser.root_rule_name:
        parser.root_rule_name = metacls_name

    return metacls_name
metaclass_name.sem = metaclass_name_SA

def alternative_match_SA(parser, node, children):
    return OrderedChoice(nodes=children[:])
alternative_match.sem = alternative_match_SA

def alternative_inher_SA(parser, node, children):
    return OrderedChoice(nodes=children[:])
alternative_inher.sem = alternative_inher_SA

def sequence_SA(parser, node, children):
    return Sequence(nodes=children[:])
sequence.sem = sequence_SA

def choice_SA(parser, node, children):
    return OrderedChoice(nodes=children[:])
choice.sem = choice_SA

def assignment_rhs_SA(parser, node, children):
    rule = children[0]
    if len(children)==1:
        return rule

    rep_op = children[1]
    if rep_op == '?':
        return Optional(nodes=[rule])
    elif rep_op == '*':
        return ZeroOrMore(nodes=[rule])
    else:
        return OneOrMore(nodes=[rule])
assignment_rhs.sem = assignment_rhs_SA

def assignment_SA(parser, node, children):
    """
    Create parser rule for addition and register attribute types
    on metaclass.
    """
    attr_name = children[0]
    op = children[1]
    rhs = children[2]
    mclass_info = parser._current_metacls_info
    mclass = mclass_info.metacls

    if parser.debug:
        print("Processing assignment {}{}...".format(attr_name, op))

    def ref_cont_store_info(ref_type, rule_crossref):
        if type(rule_crossref) is not RuleCrossRef or \
                rule_crossref.metaclass in PRIMITIVE_TYPE_NAMES:
            return
        rule_name = rule_crossref.rule_name
        target_metaclass = rule_crossref.metaclass
        minfo_list = mclass_info.cont if ref_type == "cont" else mclass_info.refs
        minfo_list.append(\
                (attr_name, MetaClassCrossRef(target_metaclass, attr_name, \
                                rule_crossref.position), '*'))

    # Keep track of metaclass references and containments
    if type(rhs) is tuple and rhs[0] in ["link", "cont"]:
        ref_cont_store_info(*rhs)
        # Override rhs by its PEG rule for further processing
        rhs = rhs[1]

    if type(rhs) is tuple:
        if rhs[0] == "list":
            # Special case. List as rhs
            _, list_el_rule, separator = rhs

            # List rule may be a ref-cont
            if type(list_el_rule) is tuple and list_el_rule[0] in ["link", "cont"]:
                ref_cont_store_info(*list_el_rule)
                list_el_rule = list_el_rule[1]

            base_rule_name = list_el_rule.rule_name
            if op == '+=':
                # If operation is += there must be at least one element in the list
                assignment_rule = Sequence(nodes=[list_el_rule,
                        OneOrMore(nodes=Sequence(nodes=[separator, list_el_rule]))],
                        rule_name='__asgn_list', root=True)
            else:
                assignment_rule = Sequence(nodes=[list_el_rule,
                        ZeroOrMore(nodes=Sequence(nodes=[separator, list_el_rule]))],
                        rule_name='__asgn_list', root=True)
            mclass_info.attrib_types[attr_name] = 'LIST'

    else:
        # Base rule name will be used to determine primitive types
        base_rule_name = rhs.rule_name

        if attr_name in mclass_info.attrib_types:
            # TODO: This constraint should be relaxed.
            raise TextXSemanticError('Multiple assignment to the same attribute "{}" at {}'\
                    .format(attr_name, parser.pos_to_linecol(node.position)))
        if op == '+=':
            assignment_rule = OneOrMore(nodes=[rhs],
                    rule_name='__asgn_oneormore', root=True)
            mclass_info.attrib_types[attr_name] = 'LIST'
        elif op == '*=':
            assignment_rule = ZeroOrMore(nodes=[rhs],
                    rule_name='__asgn_zeroormore', root=True)
            mclass_info.attrib_types[attr_name] = 'LIST'
        elif op == '?=':
            assignment_rule = Optional(nodes=[rhs],
                    rule_name='__asgn_optional', root=True)
            mclass_info.attrib_types[attr_name] = 'BOOL'
        else:
            assignment_rule = Sequence(nodes=[rhs],
                    rule_name='__asgn_plain', root=True)
            # Determine type for proper initialization
            if rhs.rule_name in PRIMITIVE_TYPE_NAMES:
                mclass_info.attrib_types[attr_name] = rhs.rule_name
            elif type(rhs) is not RuleCrossRef and isinstance(rhs, Match):
                mclass_info.attrib_types[attr_name] = 'STRING'
            else:
                mclass_info.attrib_types[attr_name] = rhs.rule_name

    assignment_rule._attr_name = attr_name
    assignment_rule._exp_str = attr_name    # For nice error reporting
    return assignment_rule
assignment.sem = assignment_SA

def expr_SA(parser, node, children):
    if len(children)>1:
        if children[1] == '?':
            return Optional(nodes=[children[0]])
        elif children[1] == '*':
            return ZeroOrMore(nodes=[children[0]])
        elif children[1] == '+':
            return OneOrMore(nodes=[children[0]])
        else:
            TextXSemanticError('Unknown repetition operand "{}" at {}'\
                    .format(children[1], str(parser.pos_to_linecol(node[1].position))))
expr.sem = expr_SA

def str_match_SA(parser, node, children):
    return StrMatch(children[0], ignore_case=parser.ignore_case)
str_match.sem = str_match_SA

def re_match_SA(parser, node, children):
    to_match = children[0]
    regex = RegExMatch(to_match, ignore_case=parser.ignore_case)
    try:
        regex.compile()
    except Exception as e:
        raise TextXSyntaxError("{} at {}".format(str(e),\
            str(parser.pos_to_linecol(node[1].position))))
    return regex
re_match.sem = re_match_SA

def rule_match_alt_SA(parser, node, children):
    rule_name = str(node)
    # This rule is used in alternative (inheritance)
    # Crossref resolving will be done in the second pass.
    parser._current_metacls_info.inh_by.append(\
            MetaClassCrossRef(metacls_name=rule_name, \
            attr_name=None,
            position=node.position))
    # Here a name of the metaclass (rule) is expected but to support
    # forward referencing we are postponing resolving to second_pass.
    return RuleCrossRef(rule_name, rule_name, node.position)
rule_match_alt.sem = rule_match_alt_SA

def rule_match_SA(parser, node, children):
    rule_name = str(node)
    # Here a name of the metaclass (rule) is expected but to support
    # forward referencing we are postponing resolving to second_pass.
    # For containments a PEG rule name and target meta-class name are
    # the same.
    return ("cont", RuleCrossRef(rule_name, rule_name, node.position))
rule_match.sem = rule_match_SA

def rule_link_SA(parser, node, children):
    # A link to some other metaclass will be the value of its name attribute.
    print("RULELINK", str(node))
    metaclass_name = children[0]
    if metaclass_name in PRIMITIVE_TYPE_NAMES:
        raise TextXSemanticError('Primitive types can not be referenced at {}.'\
                .format(node.position))
    if len(children)>1:
        rule_name = children[1]
    else:
        # Default rule for matching obj cross-refs
        rule_name = 'ID'
    return ("link", RuleCrossRef(rule_name, metaclass_name, node.position))
rule_link.sem = rule_link_SA

def list_match_SA(parser, node, children):
    match = children[0]
    if len(children)==1:
        return ("list", match)
    else:
        separator = children[1]
        separator.rule_name = 'sep'
        # At this level we do not know the type of assignment (=, +=, *=)
        # so postpone rule construction to assignment_sa
        return ("list", match, separator)
list_match.sem = list_match_SA

# Default actions
bracketed_choice.sem = SemanticActionSingleChild()


def parser_from_str(language_def, ignore_case=True, debug=False):

    if debug:
        print("*** TEXTX PARSER ***")

    # First create parser for TextX descriptions
    parser = ParserPython(textx_model, comment_def=comment,
            ignore_case=ignore_case, reduce_tree=True, debug=debug)

    # This is used during parser construction phase.
    parser._metacls_info = {
            'ID': MetaClassInfo(metacls=type('ID', (), {}), attrib_types={},
                                refs=[], cont=[], inh_by=[]),
            'BOOL': MetaClassInfo(metacls=type('BOOL', (), {}), attrib_types={},
                                refs=[], cont=[], inh_by=[]),
            'INT': MetaClassInfo(metacls=type('INT', (), {}), attrib_types={},
                                refs=[], cont=[], inh_by=[]),
            'FLOAT': MetaClassInfo(metacls=type('FLOAT', (), {}), attrib_types={},
                                refs=[], cont=[], inh_by=[]),
            'STRING': MetaClassInfo(metacls=type('STRING', (), {}), attrib_types={},
                                refs=[], cont=[], inh_by=[]),
            }

    # Builtin rules representing primitive types
    parser._peg_rules = {
            'ID': ID,
            'INT': INT,
            'FLOAT': FLOAT,
            'STRING': STRING,
            'BOOL': BOOL,
            }
    for regex in parser._peg_rules.values():
        regex.compile()
    parser.root_rule_name = None

    # Parse language description with textX parser
    try:
        parse_tree = parser.parse(language_def)
    except NoMatch as e:
        raise TextXSyntaxError(str(e))

    # Construct new parser based on the given language description.
    lang_parser = parser.getASG()

    if debug:
        # Create dot file for debuging purposes
        PMDOTExporter().exportFile(lang_parser.parser_model,\
                "{}_parser_model.dot".format(parser.root_rule_name))

    return lang_parser

def parser_from_file(file_name, ignore_case=True, debug=False):
    """
    Constructs parser from file.

    Args:
        file_name (str): A name of the file with language description in textX.
    """

    with open(file_name, 'r') as f:
        lang_desc = f.read()

    return parser_from_str(lang_desc, ignore_case, debug)




