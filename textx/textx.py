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

import re
from arpeggio import StrMatch, Optional, ZeroOrMore, OneOrMore, Sequence,\
    OrderedChoice, RegExMatch, NoMatch, EOF, ParsingExpression,\
    SemanticAction, ParserPython, SemanticActionSingleChild
from arpeggio.export import PMDOTExporter
from arpeggio import RegExMatch as _

from .exceptions import TextXSyntaxError, TextXSemanticError
from .const import MULT_ZEROORMORE, MULT_ONEORMORE, \
    MULT_OPTIONAL, RULE_MATCH, RULE_ABSTRACT


# textX grammar
def textx_model():          return ZeroOrMore(rule), EOF
def rule():                 return [abstract_rule, match_rule, common_rule,
                                    mixin_rule, expression_rule]

# Rules
def match_rule():           return class_name, ":", match_rule_body, ";"
def abstract_rule():        return class_name, ":", abstract_rule_body, ";"
def mixin_rule():           return class_name, "mixin", ":", common_rule_body, ";"
def expression_rule():      return class_name, "expression", ":", ";" # TODO
def common_rule():          return class_name, ":", common_rule_body, ";"

def match_rule_body():      return [simple_match, rule_match], OneOrMore("|",
                                    [simple_match, rule_match])
def abstract_rule_body():   return rule_match, OneOrMore("|", rule_match)
def common_rule_body():     return expression

def sequence():             return OneOrMore([match, assignment])
def match():                return [simple_match, mixin_rule_match]
def simple_match():         return [str_match, re_match]
def mixin_rule_match():     return rule_name

def expression():           return [bracketed_expression, choice],\
                                    Optional(repeat_operator, Optional(repeat_params))
def choice():               return sequence, ZeroOrMore("|", expression)
def bracketed_expression(): return '(', expression, ')'
def repeat_operator():      return ['*', '?', '+']
def repeat_params():        return '[', OneOrMore([simple_match,
                                                   'eolterm',
                                                   'onlyonce',
                                                   'onceeach']), ']'

# Assignment
def assignment():           return attribute, assignment_op, assignment_rhs
def attribute():            return ident
def assignment_op():        return ["=", "*=", "+=", "?="]
def assignment_rhs():       return [simple_match, rule_ref], Optional(repeat_params)


def str_match():            return [("'", _(r"((\\')|[^'])*"),"'"),\
                                    ('"', _(r'((\\")|[^"])*'),'"')]
def re_match():             return "/", _(r"((\\/)|[^/])*"), "/"

# Rule reference
def rule_ref():             return [rule_match, rule_link]
def rule_match():           return ident
def rule_link():            return '[', rule_name, Optional('|', rule_rule), ']'
def function_name():        return ident
def rule_name():            return ident
def rule_rule():            return ident
def class_name():           return ident

def ident():                return _(r'\w+')

# Comments
def comment():              return [comment_line, comment_block]
def comment_line():         return _(r'//.*?$')
def comment_block():        return _(r'/\*(.|\n)*?\*/')



# Special rules - primitive types
ID          = _(r'[^\d\W]\w*\b', rule_name='ID', root=True)
BOOL        = _(r'true|false|0|1', rule_name='BOOL', root=True)
INT         = _(r'[-+]?[0-9]+', rule_name='INT', root=True)
FLOAT       = _(r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?', 'FLOAT', root=True)
STRING      = _(r'("[^"]*")|(\'[^\']*\')', 'STRING', root=True)
NUMBER      = OrderedChoice(nodes=[FLOAT, INT], rule_name='NUMBER', root=True)
BASETYPE    = OrderedChoice(nodes=[ID, STRING, BOOL, NUMBER], \
                    rule_name='BASETYPE', root=True)

BASE_TYPE_RULES = {rule.rule_name: rule
                   for rule in [ID, BOOL, INT, FLOAT,
                                STRING, NUMBER, BASETYPE]}
BASE_TYPE_NAMES = BASE_TYPE_RULES.keys()

for regex in [ID, BOOL, INT, FLOAT, STRING]:
    regex.compile()


def python_type(textx_type_name):
    """Return Python type from the name of base textx type."""
    return {
        'ID': str,
        'BOOL': bool,
        'INT': int,
        'FLOAT': float,
        'STRING': str,
        'NUMBER': float,
        'BASETYPE': str,
    }.get(textx_type_name, textx_type_name)


class RuleCrossRef(object):
    """
    Used for cross reference resolving.

    Attributes:
        rule_name(str): A name of the PEG rule that should be used to match
            this cross-ref.
        cls(str or ClassCrossRef): Target class which is matched by the
            rule_name or which name is matched by the rule_name.
        position(int): A position in the input string of this cross-ref.
    """
    def __init__(self, rule_name, cls, position):
        self.rule_name = rule_name
        self.cls = cls
        self.position = position


class ClassCrossRef(object):
    """
    Used for class reference resolving on the meta-model level.

    Attributes:
        cls_name(str): A name of the target class.
        attr_name(str): The name of the attribute used for cross-referencing.
        position(int): The position in the input string of this cross-ref.
    """
    def __init__(self, cls_name, attr_name='', position=0):
        self.cls_name = cls_name
        self.attr_name = attr_name
        self.position = position


# TextX semantic actions
class TextXModelSA(SemanticAction):
    def first_pass(self, parser, node, children):
        comments_model = parser.peg_rules.get('__comment', None)

        from .model import get_model_parser
        textx_parser = get_model_parser(children[0], comments_model,
                                        parser.debug)

        textx_parser.metamodel = parser.metamodel
        textx_parser.peg_rules = parser.peg_rules

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
                    if rule_name in textx_parser.peg_rules:
                        rule = textx_parser.peg_rules[rule_name]
                    else:
                        line, col = parser.pos_to_linecol(rule.position)
                        raise TextXSemanticError(
                            'Unexisting rule "{}" at position {}.'
                            .format(rule.rule_name,
                                    (line, col)), line, col)

                assert isinstance(rule, ParsingExpression),\
                    "{}:{}".format(type(rule), str(rule))
                # Recurse
                for idx, child in enumerate(rule.nodes):
                    if child not in resolved_set:
                        resolved_set.add(rule)
                        rule.nodes[idx] = _inner_resolve(child)

                return rule

            resolved_set.add(node)
            _inner_resolve(node)

        if parser.debug:
            print("CROSS-REFS RESOLVING")

        resolve(textx_parser.parser_model)

    def _resolve_cls_refs(self, parser, xtext_parser):
        from .metamodel import TextXClass

        def _resolve_cls(cls_crossref):
            if isinstance(cls_crossref, ClassCrossRef):
                if cls_crossref.cls_name not in xtext_parser.metamodel:
                    line, col = parser.pos_to_linecol(cls_crossref.position)
                    raise TextXSemanticError(
                        'Unknown class/rule "{}" at {}.'
                        .format(cls_crossref.cls_name, (line, col)), line, col)
                return xtext_parser.metamodel[cls_crossref.cls_name]

            elif issubclass(cls_crossref, TextXClass):
                # If already resolved
                return cls_crossref

        if parser.debug:
            print("RESOLVING METACLASS REFS")

        for cls in xtext_parser.metamodel.values():

            # Inheritance
            for idx, inh in enumerate(cls._inh_by):
                cls._inh_by[idx] = _resolve_cls(inh)

            # References
            for attr in cls._attrs.values():
                attr.cls = _resolve_cls(attr.cls)

                # If target cls is of a base type or match rule
                # then attr can not be a reference.
                if attr.cls.__name__ in BASE_TYPE_NAMES \
                        or attr.cls._type == "match":
                    attr.ref = False
                    attr.cont = True
                else:
                    attr.ref = True

                if parser.debug:
                    print("Resolved attribute {}:{}[cls={}, cont={}, ref={}, mult={}, pos={}]"
                          .format(cls.__name__, attr.name, attr.cls.__name__,
                                  attr.cont, attr.ref, attr.mult, attr.position))

    def second_pass(self, parser, textx_parser):
        """Cross reference resolving for parser model."""

        if parser.debug:
            print("RESOLVING XTEXT PARSER: second_pass")

        self._resolve_rule_refs(parser, textx_parser)
        self._resolve_cls_refs(parser, textx_parser)

        return textx_parser
textx_model.sem = TextXModelSA()


def rule_SA(parser, node, children):
    rule_name, rule = children
    rule = Sequence(nodes=[rule], rule_name=rule_name,
                    root=True)

    # Do some name mangling for comment rule
    # to prevent refererencing from other rules
    if rule_name.lower() == "comment":
        rule_name = "__comment"

    parser.peg_rules[rule_name] = rule
    return rule
rule.sem = rule_SA


def class_name_SA(parser, node, children):

    cls_name = str(node)
    if parser.debug:
        print("Creating class: {}".format(cls_name))

    cls = parser.metamodel.new_class(cls_name, node.position)

    parser._current_cls = cls

    # First class will be the root of the meta-model
    if not parser.metamodel.rootcls:
        parser.metamodel.rootcls = cls

    return cls_name
class_name.sem = class_name_SA


def match_rule_body_SA(parser, node, children):
    # This is a match rule
    parser._current_cls._type = RULE_MATCH
    # String representation of match alternatives.
    # Used in visualizations and debugging
    parser._current_cls._match_str = "|".join([str(match)
                                              for match in children])
    return OrderedChoice(nodes=children[:])
match_rule_body.sem = match_rule_body_SA


def abstract_rule_body_SA(parser, node, children):
    # This is an abstract rule
    parser._current_cls._type = RULE_ABSTRACT
    return OrderedChoice(nodes=children[:])
abstract_rule_body.sem = abstract_rule_body_SA


def sequence_SA(parser, node, children):
    return Sequence(nodes=children[:])
sequence.sem = sequence_SA


def choice_SA(parser, node, children):
    return OrderedChoice(nodes=children[:])
choice.sem = choice_SA


def assignment_rhs_SA(parser, node, children):
    rule = children[0]
    if len(children) == 1:
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
    cls = parser._current_cls
    target_cls = None

    if parser.debug:
        print("Processing assignment {}{}...".format(attr_name, op))

    if parser.debug:
        print("Creating attribute {}:{}".format(cls.__name__, attr_name))
    if attr_name in cls._attrs:
        # TODO: This constraint should be relaxed.
        line, col = parser.pos_to_linecol(node.position)
        raise TextXSemanticError(
            'Multiple assignment to the same attribute "{}" at {}'
            .format(attr_name, (line, col)), line, col)

    cls_attr = cls.new_attr(name=attr_name, position=node.position)

    # Keep track of metaclass references and containments
    if type(rhs) is tuple and rhs[0] == "link":
        cls_attr.cont = False
        cls_attr.ref = True
        # Override rhs by its PEG rule for further processing
        rhs = rhs[1]
        # Target class is not the same as target rule
        target_cls = rhs.cls

    if type(rhs) is tuple:
        if rhs[0] == "list":
            # Special case. List as rhs
            _, list_el_rule, separator = rhs

            # List rule may be a ref-cont
            if type(list_el_rule) is tuple and list_el_rule[0] == "link":
                cls_attr.cont = False
                cls_attr.ref = True
                list_el_rule = list_el_rule[1]
                # Target class is not the same as target rule
                target_cls = list_el_rule.cls

            base_rule_name = list_el_rule.rule_name
            if op == '+=':
                # If operation is += there must be at least one element
                # in the list
                assignment_rule = Sequence(
                    nodes=[list_el_rule,
                           ZeroOrMore(nodes=Sequence(nodes=[separator,
                                                            list_el_rule]))],
                    rule_name='__asgn_list', root=True)

                cls_attr.mult = MULT_ONEORMORE
            else:
                assignment_rule = Optional(
                    nodes=[Sequence(nodes=[list_el_rule,
                           ZeroOrMore(nodes=Sequence(nodes=[separator,
                                                            list_el_rule]))])],
                    rule_name='__asgn_list', root=True)

                cls_attr.mult = MULT_ZEROORMORE
            rhs = list_el_rule
            base_rule_name = rhs.rule_name
    else:
        base_rule_name = rhs.rule_name
        if op == '+=':
            assignment_rule = OneOrMore(
                nodes=[rhs],
                rule_name='__asgn_oneormore', root=True)
            cls_attr.mult = MULT_ONEORMORE
        elif op == '*=':
            assignment_rule = ZeroOrMore(
                nodes=[rhs],
                rule_name='__asgn_zeroormore', root=True)
            cls_attr.mult = MULT_ZEROORMORE
        elif op == '?=':
            assignment_rule = Optional(
                nodes=[rhs],
                rule_name='__asgn_optional', root=True)
            cls_attr.mult = MULT_OPTIONAL
            base_rule_name = 'BOOL'
        else:
            assignment_rule = Sequence(
                nodes=[rhs],
                rule_name='__asgn_plain', root=True)

    if target_cls:
        attr_type = target_cls
    else:
        # Use STRING as default attr class
        attr_type = base_rule_name if base_rule_name else 'STRING'
    cls_attr.cls = ClassCrossRef(cls_name=attr_type, position=node.position)

    if parser.debug:
        print("Created attribute {}:{}[cls={}, cont={}, ref={}, mult={}, pos={}]"
              .format(cls.__name__, attr_name, cls_attr.cls.cls_name,
                      cls_attr.cont, cls_attr.ref, cls_attr.mult, cls_attr.position))

    assignment_rule._attr_name = attr_name
    assignment_rule._exp_str = attr_name    # For nice error reporting
    return assignment_rule
assignment.sem = assignment_SA


def expr_SA(parser, node, children):
    if len(children) > 1:
        if children[1] == '?':
            return Optional(nodes=[children[0]])
        elif children[1] == '*':
            return ZeroOrMore(nodes=[children[0]])
        elif children[1] == '+':
            return OneOrMore(nodes=[children[0]])
        else:
            line, col = parser.pos_to_linecol(node[1].position)
            TextXSemanticError(
                'Unknown repetition operand "{}" at {}'
                .format(children[1],
                        str((line, col))), line, col)
expr.sem = expr_SA


def str_match_SA(parser, node, children):
    to_match = children[0]
    # Special case. If to_match is a keyword-like string
    # matching should be done with word boundaries on.
    # If this is not done we can run into problems described
    # in the test test_match_whole_word
    match = parser.keyword_regex.match(to_match)
    if match and match.span() == (0, len(to_match)):
        regex_match = RegExMatch(r'{}\b'.format(to_match),
                                 ignore_case=parser.ignore_case)
        regex_match.compile()
        return regex_match
    else:
        return StrMatch(to_match, ignore_case=parser.ignore_case)
str_match.sem = str_match_SA


def re_match_SA(parser, node, children):
    to_match = children[0]
    regex = RegExMatch(to_match, ignore_case=parser.ignore_case)
    try:
        regex.compile()
    except Exception as e:
        line, col = parser.pos_to_linecol(node[1].position)
        raise TextXSyntaxError(
            "{} at {}"
            .format(str(e), str((line, col))), line, col)
    return regex
re_match.sem = re_match_SA


def rule_match_alt_SA(parser, node, children):
    rule_name = str(node)
    # This rule is used in alternative (inheritance)
    # Crossref resolving will be done in the second pass.
    parser._current_cls._inh_by.append(
        ClassCrossRef(cls_name=rule_name,
                      attr_name=None,
                      position=node.position))
    # Here a name of the class (rule) is expected but to support
    # forward referencing we are postponing resolving to second_pass.
    return RuleCrossRef(rule_name, rule_name, node.position)
rule_match_alt.sem = rule_match_alt_SA


def rule_match_SA(parser, node, children):
    rule_name = str(node)
    # Here a name of the metaclass (rule) is expected but to support
    # forward referencing we are postponing resolving to second_pass.
    return RuleCrossRef(rule_name, rule_name, node.position)
rule_match.sem = rule_match_SA


def rule_link_SA(parser, node, children):
    # A link to some other class will be the value of its "name" attribute.
    class_name = children[0]
    if class_name in BASE_TYPE_NAMES:
        line, col = parser.pos_to_linecol(node.position)
        raise TextXSemanticError(
            'Primitive types can not be referenced at {}.'
            .format((line, col)), line, col)
    if len(children) > 1:
        rule_name = children[1]
    else:
        # Default rule for matching obj cross-refs
        rule_name = 'ID'
    return ("link", RuleCrossRef(rule_name, class_name, node.position))
rule_link.sem = rule_link_SA


def list_match_SA(parser, node, children):
    match = children[0]
    if len(children) == 1:
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


def language_from_str(language_def, metamodel, ignore_case=True, debug=False):
    """
    Constructs parser and initializes metamodel from language description
    given in textX file.

    Args:
        language_def (str): A language description in textX.
        metamodel (TextXMetaModel): A metamodel to initialize.

    Returns:
        Parser for the new language.
    """

    if debug:
        print("*** TEXTX PARSER ***")

    # First create parser for TextX descriptions
    parser = ParserPython(textx_model, comment_def=comment,
                          ignore_case=ignore_case,
                          reduce_tree=True, debug=debug)

    # Prepare regex used in keyword-like strmatch detection.
    # See str_match_SA
    flags = 0
    if ignore_case:
        flags = re.IGNORECASE
    parser.keyword_regex = re.compile(r'[^\d\W]\w*', flags)

    # This is used during parser construction phase.
    parser.metamodel = metamodel

    # Builtin rules representing primitive types
    parser.peg_rules = dict(BASE_TYPE_RULES)
    parser.root_rule_name = None

    # Parse language description with textX parser
    try:
        parser.parse(language_def)
    except NoMatch as e:
        line, col = parser.pos_to_linecol(e.position)
        raise TextXSyntaxError(str(e), line, col)

    # Construct new parser based on the given language description.
    lang_parser = parser.getASG()

    # Metamodel is constructed. Here we connect metamodel and language
    # parser for convenience.
    lang_parser.metamodel = parser.metamodel
    metamodel.parser = lang_parser

    if debug:
        # Create dot file for debuging purposes
        PMDOTExporter().exportFile(
            lang_parser.parser_model,
            "{}_parser_model.dot".format(metamodel.rootcls.__name__))

    return lang_parser



