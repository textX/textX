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
    OrderedChoice, RegExMatch, Match, NoMatch, EOF, ParsingExpression,\
    SemanticAction, ParserPython, SemanticActionSingleChild
from arpeggio.export import PMDOTExporter
from arpeggio import RegExMatch as _

from .exceptions import TextXSyntaxError, TextXSemanticError
from .const import MULT_ZEROORMORE, MULT_ONEORMORE, \
    MULT_OPTIONAL, RULE_MATCH, RULE_ABSTRACT


# textX grammar
def textx_model():          return ZeroOrMore(textx_rule), EOF
# def textx_rule():           return [abstract_rule, match_rule, common_rule,
#                                     mixin_rule, expression_rule]

def textx_rule():           return [abstract_rule, match_rule, common_rule]
# Rules
def common_rule():          return rule_name, ":", common_rule_body, ";"
def match_rule():           return rule_name, ":", match_rule_body, ";"
def abstract_rule():        return rule_name, ":", abstract_rule_body, ";"
def mixin_rule():           return rule_name, "mixin", ":", common_rule_body, ";" #TODO
def expression_rule():      return rule_name, "expression", ":", ";" # TODO

def common_rule_body():     return choice
def match_rule_body():      return [simple_match, rule_ref], OneOrMore("|",
                                    [simple_match, rule_ref])
def abstract_rule_body():   return abstract_rule_ref, OneOrMore("|", abstract_rule_ref)

def sequence():             return OneOrMore([assignment, repeatable_expr])
def repeatable_expr():      return [bracketed_choice, simple_match, rule_ref],\
                                    Optional(repeat_operator)
# def match():                return [simple_match , mixin_rule_match] TODO
def simple_match():         return [str_match, re_match]

def choice():               return sequence, ZeroOrMore("|", sequence)
def bracketed_choice():     return '(', choice, ')'
def repeat_operator():      return ['*', '?', '+'], Optional(repeat_modifiers)
def repeat_modifiers():     return '[', OneOrMore([simple_match,
                                                   multiplicity,
                                                   'eolterm']), ']'
def multiplicity():         return integer, Optional('..', integer)

# Assignment
def assignment():           return attribute, assignment_op, assignment_rhs
def attribute():            return ident
def assignment_op():        return ["=", "*=", "+=", "?="]
def assignment_rhs():       return [simple_match, reference], Optional(repeat_modifiers)

# References
def reference():            return [rule_ref, obj_ref]
def rule_ref():             return ident
def abstract_rule_ref():    return ident
def obj_ref():              return '[', class_name, Optional('|', obj_ref_rule), ']'

def rule_name():            return ident
def obj_ref_rule():         return ident
def class_name():           return ident

def str_match():            return [("'", _(r"((\\')|[^'])*"),"'"),\
                                    ('"', _(r'((\\")|[^"])*'),'"')]
def re_match():             return "/", _(r"((\\/)|[^/])*"), "/"
def ident():                return _(r'\w+')
def integer():              return _(r'[-+]?[0-9]+')

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
    Used during meta-model parser construction for cross reference resolving
    of PEG rules, to support forward references.

    Attributes:
        rule_name(str): A name of the PEG rule that should be used to match
            this cross-ref.
        cls(str or ClassCrossRef): Target class which is matched by the
            rule_name or which name is matched by the rule_name.
            Used for rule references in the RHS of the assignments to
            determine attribute type.
        position(int): A position in the input string of this cross-ref.
    """
    def __init__(self, rule_name, cls, position):
        self.rule_name = rule_name
        self.cls = cls
        self.position = position


class ClassCrossRef(object):
    """
    Used for class reference resolving on the meta-model level.
    References will be resolved after semantic analysis of the meta-model
    parse tree. After resolving phase the meta-model will be fully linked.

    Attributes:
        cls_name(str): A name of the target meta-model class.
        position(int): The position in the input string of this cross-ref.
    """
    def __init__(self, cls_name, position=0):
        self.cls_name = cls_name
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


def textx_rule_SA(parser, node, children):
    rule_name, rule = children[0]
    rule = Sequence(nodes=[rule], rule_name=rule_name,
                    root=True)

    # Do some name mangling for comment rule
    # to prevent referencing from other rules
    if rule_name.lower() == "comment":
        rule_name = "__comment"

    parser.peg_rules[rule_name] = rule
    return rule
textx_rule.sem = textx_rule_SA


def rule_name_SA(parser, node, children):

    cls_name = str(node)
    if parser.debug:
        print("Creating class: {}".format(cls_name))

    cls = parser.metamodel.new_class(cls_name, node.position)

    parser._current_cls = cls

    # First class will be the root of the meta-model
    if not parser.metamodel.rootcls:
        parser.metamodel.rootcls = cls

    return cls_name
rule_name.sem = rule_name_SA


def rules(parser, node, children):
    return (children[0], children[1])
common_rule.sem = rules
abstract_rule.sem = rules
match_rule.sem = rules


def match_rule_body_SA(parser, node, children):
    # This is a match rule
    parser._current_cls._type = RULE_MATCH
    # String representation of match alternatives.
    # Used in visualizations and debugging
    parser._current_cls._match_str = "|".join([str(match)
                                              for match in children])
    return OrderedChoice(nodes=children[:])
match_rule_body.sem = match_rule_body_SA


def rule_ref_SA(parser, node, children):
    rule_name = str(node)
    # Here a name of the meta-class (rule) is expected but to support
    # forward referencing we are postponing resolving to second_pass.
    return RuleCrossRef(rule_name, rule_name, node.position)
rule_ref.sem = rule_ref_SA


def abstract_rule_body_SA(parser, node, children):
    # This is a body of an abstract rule so set
    # the proper type
    parser._current_cls._type = RULE_ABSTRACT
    return OrderedChoice(nodes=children[:])
abstract_rule_body.sem = abstract_rule_body_SA


def abstract_rule_ref_SA(parser, node, children):
    rule_name = str(node)
    # This rule is used in alternative (inheritance)
    # Crossref resolving will be done in the second pass.
    parser._current_cls._inh_by.append(
        ClassCrossRef(cls_name=rule_name,
                      position=node.position))
    # Here a name of the class (rule) is expected but to support
    # forward referencing we are postponing resolving to second_pass.
    return RuleCrossRef(rule_name, rule_name, node.position)
abstract_rule_ref.sem = abstract_rule_ref_SA


def sequence_SA(parser, node, children):
    return Sequence(nodes=children[:])
sequence.sem = sequence_SA


def choice_SA(parser, node, children):
    return OrderedChoice(nodes=children[:])
choice.sem = choice_SA


def multiplicity_SA(parser, node, children):
    if len(children) == 2:
        return (int(children[0]), int(children[1]))
    else:
        return (int(children[0]), int(children[0]))
multiplicity.sem = multiplicity_SA


def repeat_modifiers_SA(parser, node, children):
    modifiers = {}
    for modifier in children:
        if isinstance(modifier, Match):
            # Separator
            modifier.rule_name = 'sep'
            modifiers['sep'] = modifier
        elif type(modifier) == tuple:
            modifiers['multiplicity'] = modifier
        else:
            modifiers['eolterm'] = True
    return (modifiers, node.position)
repeat_modifiers.sem = repeat_modifiers_SA


def repeat_operator_SA(parser, node, children):
    return children
repeat_operator.sem = repeat_operator_SA


def repeatable_expr_SA(parser, node, children):
    expr = children[0]
    rule = expr
    if len(children) > 1:
        repeat_op = children[1]
        if len(repeat_op) > 1:
            repeat_op, modifiers = repeat_op
        else:
            modifiers = None

        if repeat_op == '?':
            rule = Optional(nodes=[expr])
        elif repeat_op == '*':
            rule = ZeroOrMore(nodes=[expr])
        else:
            rule = OneOrMore(nodes=[expr])

        if modifiers:
            modifiers, position = modifiers
            # Sanity check. Modifiers do not make
            # sense for ? operator at the moment.
            if repeat_op == '?':
                line, col = parser.pos_to_linecol(position)
                raise TextXSyntaxError('Modifiers are not allowed for "?" operator at {}'\
                        .format(str((line, col))), line, col)
            # Separator modifier
            if 'sep' in modifiers:
                sep = modifiers['sep']
                rule = Sequence(nodes=[expr,
                                ZeroOrMore(nodes=[Sequence(nodes=[sep, expr])])])
                if repeat_op == "*":
                    rule = Optional(nodes=[rule])

            # End of line termination modifier
            if 'eolterm' in modifiers:
                rule.eolterm = True

    return rule
repeatable_expr.sem = repeatable_expr_SA


def assignment_rhs_SA(parser, node, children):
    rule = children[0]
    modifiers = None
    if len(children) > 1:
        modifiers = children[1]

    # At this level we do not know the type of assignment (=, +=, *=)
    # and we do not have access to the PEG rule so postpone
    # rule modification for assignment semantic action.
    return (rule, modifiers)
assignment_rhs.sem = assignment_rhs_SA


def assignment_SA(parser, node, children):
    """
    Create parser rule for addition and register attribute types
    on metaclass.
    """
    attr_name = children[0]
    op = children[1]
    rhs_rule, modifiers = children[2]
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
    if type(rhs_rule) is tuple and rhs_rule[0] == "obj_ref":
        cls_attr.cont = False
        cls_attr.ref = True
        # Override rhs by its PEG rule for further processing
        rhs_rule = rhs_rule[1]
        # Target class is not the same as target rule
        target_cls = rhs_rule.cls

    base_rule_name = rhs_rule.rule_name
    if op == '+=':
        assignment_rule = OneOrMore(
            nodes=[rhs_rule],
            rule_name='__asgn_oneormore', root=True)
        cls_attr.mult = MULT_ONEORMORE
    elif op == '*=':
        assignment_rule = ZeroOrMore(
            nodes=[rhs_rule],
            rule_name='__asgn_zeroormore', root=True)
        cls_attr.mult = MULT_ZEROORMORE
    elif op == '?=':
        assignment_rule = Optional(
            nodes=[rhs_rule],
            rule_name='__asgn_optional', root=True)
        cls_attr.mult = MULT_OPTIONAL
        base_rule_name = 'BOOL'
    else:
        assignment_rule = Sequence(
            nodes=[rhs_rule],
            rule_name='__asgn_plain', root=True)

    # Modifiers
    if modifiers:
        modifiers, position = modifiers
        # Sanity check. Modifiers do not make
        # sense for ?= operator at the moment.
        if op == '?=':
            line, col = parser.pos_to_linecol(position)
            raise TextXSyntaxError(
                'Modifiers are not allowed for "?=" operator at {}'
                .format(str((line, col))), line, col)

        # Separator modifier
        if 'sep' in modifiers:
            sep = modifiers['sep']
            assignment_rule = Sequence(
                nodes=[rhs_rule,
                       ZeroOrMore(nodes=[Sequence(nodes=[sep, rhs_rule])])],
                rule_name='__asgn_list', root=True)
            if op == "*=":
                assignment_rule = Optional(nodes=[rhs_rule])
                assignment_rule = Optional(nodes=[Sequence(
                    nodes=[rhs_rule,
                           ZeroOrMore(nodes=[
                               Sequence(nodes=[sep, rhs_rule])])])],
                    rule_name='__asgn_list', root=True)

        # End of line termination modifier
        if 'eolterm' in modifiers:
            assignment_rule.eolterm = True

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


def obj_ref_SA(parser, node, children):
    # A reference to some other class instance will be the value of
    # its "name" attribute.
    class_name = children[0]
    if class_name in BASE_TYPE_NAMES:
        line, col = parser.pos_to_linecol(node.position)
        raise TextXSemanticError(
            'Primitive type instances can not be referenced at {}.'
            .format((line, col)), line, col)
    if len(children) > 1:
        rule_name = children[1]
    else:
        # Default rule for matching obj cross-refs
        rule_name = 'ID'
    return ("obj_ref", RuleCrossRef(rule_name, class_name, node.position))
obj_ref.sem = obj_ref_SA


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

    # First create parser for TextX descriptions from
    # the textX grammar specified in this module
    parser = ParserPython(textx_model, comment_def=comment,
                          ignore_case=ignore_case,
                          reduce_tree=False, debug=debug)

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

    # Meta-model is constructed. Here we connect meta-model and language
    # parser for convenience.
    lang_parser.metamodel = parser.metamodel
    metamodel.parser = lang_parser

    if debug:
        # Create dot file for debuging purposes
        PMDOTExporter().exportFile(
            lang_parser.parser_model,
            "{}_parser_model.dot".format(metamodel.rootcls.__name__))

    return lang_parser

