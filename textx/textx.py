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

from __future__ import unicode_literals
import sys
if sys.version < '3':
    text = unicode
else:
    text = str

import re
from arpeggio import StrMatch, Optional, ZeroOrMore, OneOrMore, Sequence,\
    OrderedChoice, Not, And, RegExMatch, Match, NoMatch, EOF, \
    ParsingExpression, SemanticAction, ParserPython, SemanticActionSingleChild
from arpeggio.export import PMDOTExporter
from arpeggio import RegExMatch as _

from .exceptions import TextXSyntaxError, TextXSemanticError
from .const import MULT_ZEROORMORE, MULT_ONEORMORE, \
    MULT_OPTIONAL, RULE_COMMON, RULE_MATCH, RULE_ABSTRACT


# textX grammar
def textx_model():          return ZeroOrMore(import_stm), ZeroOrMore(textx_rule), EOF

def import_stm():           return 'import', grammar_to_import
def grammar_to_import():    return _(r'(\w|\.)+')

# Rules
def textx_rule():           return rule_name, Optional(rule_params), ":", textx_rule_body, ";"
def rule_params():          return '[', rule_param, ZeroOrMore(',', rule_param), ']'
def rule_param():           return param_name, Optional('=', string_value)
def param_name():           return ident
def textx_rule_body():      return sequence

def sequence():             return OneOrMore(choice)
def choice():               return repeatable_expr, ZeroOrMore("|", repeatable_expr)
def repeatable_expr():      return expression, Optional(repeat_operator), Optional('-')
def expression():           return [assignment, (Optional(syntactic_predicate),
                                                 [simple_match, rule_ref,
                                                  bracketed_sequence])]
def bracketed_sequence():   return '(', sequence, ')'
def repeat_operator():      return ['*', '?', '+'], Optional(repeat_modifiers)
def repeat_modifiers():     return '[', OneOrMore([simple_match,
                                                   'eolterm']), ']'
def syntactic_predicate():  return ['!', '&']
def simple_match():         return [str_match, re_match]

# Assignment
def assignment():           return attribute, assignment_op, assignment_rhs
def attribute():            return ident
def assignment_op():        return ["=", "*=", "+=", "?="]
def assignment_rhs():       return [simple_match, reference], Optional(repeat_modifiers)

# References
def reference():            return [rule_ref, obj_ref]
def rule_ref():             return ident
def obj_ref():              return '[', class_name, Optional('|', obj_ref_rule), ']'

def rule_name():            return ident
def obj_ref_rule():         return ident
def class_name():           return ident

def str_match():            return [("'", _(r"((\\')|[^'])*"),"'"),\
                                    ('"', _(r'((\\")|[^"])*'),'"')]
def re_match():             return "/", _(r"((\\/)|[^/])*"), "/"
def ident():                return _(r'\w+')
def integer():              return _(r'[-+]?[0-9]+')
def string_value():         return [_(r"'((\\')|[^'])*'"),
                                    _(r'"((\\")|[^"])*"')]

# Comments
def comment():              return [comment_line, comment_block]
def comment_line():         return _(r'//.*?$')
def comment_block():        return _(r'/\*(.|\n)*?\*/')



# Special rules - primitive types
ID          = _(r'[^\d\W]\w*\b', rule_name='ID', root=True)
BOOL        = _(r'(True|true|False|false|0|1)\b', rule_name='BOOL', root=True)
INT         = _(r'[-+]?[0-9]+\b', rule_name='INT', root=True)
FLOAT       = _(r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\b', 'FLOAT', root=True)
STRING      = _(r'("(\\"|[^"])*")|(\'(\\\'|[^\'])*\')', 'STRING', root=True)
NUMBER      = OrderedChoice(nodes=[FLOAT, INT], rule_name='NUMBER', root=True)
BASETYPE    = OrderedChoice(nodes=[NUMBER, BOOL, ID, STRING],
                            rule_name='BASETYPE', root=True)

BASE_TYPE_RULES = {rule.rule_name: rule
                   for rule in [ID, BOOL, INT, FLOAT,
                                STRING, NUMBER, BASETYPE]}
BASE_TYPE_NAMES = BASE_TYPE_RULES.keys()

PRIMITIVE_PYTHON_TYPES = [int, float, text, bool]

for regex in [ID, BOOL, INT, FLOAT, STRING]:
    regex.compile()


def python_type(textx_type_name):
    """Return Python type from the name of base textx type."""
    return {
        'ID': text,
        'BOOL': bool,
        'INT': int,
        'FLOAT': float,
        'STRING': text,
        'NUMBER': float,
        'BASETYPE': text,
    }.get(textx_type_name, textx_type_name)


class RuleCrossRef(object):
    """
    Used during meta-model parser construction for cross reference resolving
    of PEG rules, to support forward references.

    Attributes:
        rule_name(str): A name of the PEG rule that should be used to match
            this cross-ref. For link rule references it will be ID by default.
        cls(str or ClassCrossRef): Target class which is matched by the
            rule_name rule or which name is matched by the rule_name rule (for
            link rule references).
            Used for rule references in the RHS of the assignments to
            determine attribute type.
        position(int): A position in the input string of this cross-ref.
    """
    def __init__(self, rule_name, cls, position):
        self.rule_name = rule_name
        self.cls = cls
        self.position = position
        self.suppress = False

    def __str__(self):
        return self.rule_name

    def __unicode__(self):
        return self.__str__()


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
    def first_pass(self, grammar_parser, node, children):

        metamodel = grammar_parser.metamodel

        if 'Comment' in metamodel:
            comments_model = grammar_parser.metamodel['Comment']._tx_peg_rule
        else:
            comments_model = None

        root_rule = children[0]
        from .model import get_model_parser
        model_parser = get_model_parser(root_rule, comments_model,
                                        ignore_case=metamodel.ignore_case,
                                        skipws=metamodel.skipws,
                                        ws=metamodel.ws,
                                        autokwd=metamodel.autokwd,
                                        debug=metamodel.debug)

        model_parser.metamodel = metamodel

        return model_parser

    def _resolve_rule_refs(self, grammar_parser, model_parser):
        """Resolves parser ParsingExpression crossrefs."""

        resolved_set = set()

        def resolve(node, cls_rule_name):
            """
            Recursively resolve peg rule references and textx rule types.

            Args:
                node(ParsingExpression or RuleCrossRef)
                cls_rule_name(str): The name of corresponding class/rule.
            """

            def _inner_resolve(rule, cls_rule_name=None):
                if grammar_parser.debug:
                    grammar_parser.dprint("Resolving rule: {}".format(rule))

                # Save initial rule name to detect special abstract rule case.
                initial_rule_name = cls_rule_name \
                    if cls_rule_name else rule.rule_name

                if type(rule) is RuleCrossRef:
                    rule_name = rule.rule_name
                    suppress = rule.suppress
                    if rule_name in model_parser.metamodel:
                        rule = model_parser.metamodel[rule_name]._tx_peg_rule
                        if type(rule) is RuleCrossRef:
                            rule = _inner_resolve(rule)
                            model_parser.metamodel[rule_name]\
                                ._tx_peg_rule = rule
                        if suppress:
                            # Special case. Suppression on rule reference.
                            _tx_class = rule._tx_class
                            rule = Sequence(nodes=[rule],
                                            rule_name=rule_name,
                                            suppress=suppress)
                            rule._tx_class = _tx_class
                    else:
                        line, col = grammar_parser.pos_to_linecol(rule.position)
                        raise TextXSemanticError(
                            'Unexisting rule "{}" at position {}.'
                            .format(rule.rule_name,
                                    (line, col)), line, col)

                assert isinstance(rule, ParsingExpression),\
                    "{}:{}".format(type(rule), text(rule))

                # If there is meta-class attributes collected than this
                # is a common rule
                if hasattr(rule, '_tx_class') and \
                        len(rule._tx_class._tx_attrs) > 0:
                    rule._tx_class._tx_type = RULE_COMMON

                # Recurse into subrules, resolve and determine rule types.
                for idx, child in enumerate(rule.nodes):
                    if child not in resolved_set:
                        resolved_set.add(rule)
                        child = _inner_resolve(child)
                        rule.nodes[idx] = child

                # Check if this rule is abstract
                # Abstract are root rules which haven't got any attributes
                # and reference at least one non-match rule.
                if initial_rule_name in model_parser.metamodel:
                    cls =  model_parser.metamodel[initial_rule_name]
                    abstract = False
                    if rule.rule_name and initial_rule_name != rule.rule_name:
                        abstract = model_parser.metamodel[rule.rule_name]._tx_type != RULE_MATCH
                    else:
                        abstract = not cls._tx_attrs and \
                            any([c._tx_class._tx_type != RULE_MATCH
                                for c in rule.nodes if hasattr(c, '_tx_class')])

                    if abstract:
                        cls._tx_type = RULE_ABSTRACT
                        # Add inherited classes to this rule's meta-class
                        if rule.rule_name and initial_rule_name != rule.rule_name:
                            if rule._tx_class not in cls._tx_inh_by:
                                cls._tx_inh_by.append(rule._tx_class)
                        else:
                            for idx, child in enumerate(rule.nodes):
                                if child.root and hasattr(child, '_tx_class'):
                                    if child._tx_class not in cls._tx_inh_by:
                                        cls._tx_inh_by.append(child._tx_class)

                return rule

            resolved_set.add(node)
            return _inner_resolve(node, cls_rule_name)

        if grammar_parser.debug:
            grammar_parser.dprint("RESOLVING RULE CROSS-REFS")

        for cls in model_parser.metamodel:
            cls._tx_peg_rule = resolve(cls._tx_peg_rule, cls.__name__)

    def _resolve_cls_refs(self, grammar_parser, model_parser):

        resolved_classes = {}

        def _resolve_cls(cls):

            if cls in resolved_classes:
                return resolved_classes[cls]

            metamodel = model_parser.metamodel

            to_resolve = cls
            if isinstance(cls, ClassCrossRef):
                if cls.cls_name not in metamodel:
                    line, col = grammar_parser.pos_to_linecol(cls.position)
                    raise TextXSemanticError(
                        'Unknown class/rule "{}" at {}.'
                        .format(cls.cls_name, (line, col)), line, col)
                cls = metamodel[cls.cls_name]
            resolved_classes[to_resolve] = cls

            if cls._tx_type == RULE_ABSTRACT:
                # Resolve inherited classes
                for idx, inh in enumerate(cls._tx_inh_by):
                    inh = _resolve_cls(inh)
                    cls._tx_inh_by[idx] = inh

            else:

                # If this is not abstract class than it must be common or match.
                # Resolve referred classes.
                # If there is no attributes collected than it ``
                for attr in cls._tx_attrs.values():
                    attr.cls = _resolve_cls(attr.cls)

                    # If target cls is of a base type or match rule
                    # then attr can not be a reference.
                    if attr.cls.__name__ in BASE_TYPE_NAMES \
                            or attr.cls._tx_type == RULE_MATCH:
                        attr.ref = False
                        attr.cont = True
                    else:
                        attr.ref = True

                    if grammar_parser.debug:
                        grammar_parser.dprint(
                            "Resolved attribute {}:{}[cls={}, cont={}, "
                            "ref={}, mult={}, pos={}]"
                            .format(cls.__name__, attr.name,
                                    attr.cls.__name__,
                                    attr.cont, attr.ref, attr.mult,
                                    attr.position))

            return cls


        if grammar_parser.debug:
            grammar_parser.dprint("RESOLVING METACLASS REFS")

        for cls in model_parser.metamodel:
            _resolve_cls(cls)

    def second_pass(self, grammar_parser, model_parser):
        """Cross reference resolving for parser model."""

        if grammar_parser.debug:
            grammar_parser.dprint("RESOLVING MODEL PARSER: second_pass")

        self._resolve_rule_refs(grammar_parser, model_parser)
        self._resolve_cls_refs(grammar_parser, model_parser)

        return model_parser
textx_model.sem = TextXModelSA()


def import_stm_SA(parser, node, children):
    parser.metamodel._new_import(children[0])
import_stm.sem = import_stm_SA


def grammar_to_import_SA(parser, node, children):
    return text(node)
grammar_to_import.sem = grammar_to_import_SA


def textx_rule_SA(parser, node, children):
    if len(children) > 2:
        rule_name, rule_params, rule = children
    else:
        rule_name, rule = children
        rule_params = {}

    if rule.rule_name.startswith('__asgn') or\
            (isinstance(rule, Match) and rule_params):
        # If it is assignment node it must be kept because it could be
        # e.g., single assignment in the rule.
        # Also, handle a special case where rule consists only of a single match
        # and there are rule modifiers defined.
        rule = Sequence(nodes=[rule], rule_name=rule_name,
                        root=True, **rule_params)
    else:
        if not isinstance(rule, RuleCrossRef):
            # Promote rule node to root node.
            rule.rule_name = rule_name
            rule.root = True
            for param in rule_params:
                setattr(rule, param, rule_params[param])

    # Connect meta-class and the PEG rule
    parser.metamodel._set_rule(rule_name, rule)

    return rule
textx_rule.sem = textx_rule_SA


def rule_name_SA(parser, node, children):
    rule_name = str(node)

    if parser.debug:
        parser.dprint("Creating class: {}".format(rule_name))

    # If a class is given by the user use it. Else, create new class.
    if rule_name in parser.metamodel.user_classes:

        cls = parser.metamodel.user_classes[rule_name]

        # Initialize special attributes
        parser.metamodel._init_class(cls, None, node.position)
    else:
        # Create class to collect attributes. At this time PEG rule
        # is not known.
        cls = parser.metamodel._new_class(rule_name, None, node.position)

    parser._current_cls = cls

    # First class will be the root of the meta-model
    if not parser.metamodel.rootcls:
        parser.metamodel.rootcls = cls

    return rule_name
rule_name.sem = rule_name_SA


def rule_params_SA(parser, node, children):
    params = {}
    for name, value in children[0].items():
        if name not in ['skipws', 'ws']:
            raise TextXSyntaxError(
                'Invalid rule param "{}" at {}.'
                .format(name, parser.pos_to_linecol(node.position)))

        if name == 'ws' and '\\' in value:
            new_value = ""
            if "\\n" in value:
                new_value += "\n"
            if "\\r" in value:
                new_value += "\r"
            if "\\t" in value:
                new_value += "\t"
            if " " in value:
                new_value += " "
            value = new_value

        params[name] = value

    return params
rule_params.sem = rule_params_SA


def rule_param_SA(parser, node, children):
    if len(children) > 1:
        param_name, param_value = children
    else:
        param_name = children[0]
        param_value = True
        if param_name.startswith('no'):
            param_name = param_name[2:]
            param_value = False

    if parser.debug:
        parser.dprint("TextX rule param: {}, {}".format(param_name,
                                                        param_value))

    return {param_name: param_value}
rule_param.sem = rule_param_SA


def rule_ref_SA(parser, node, children):
    rule_name = text(node)
    # Here a name of the meta-class (rule) is expected but to support
    # forward referencing we are postponing resolving to second_pass.
    return RuleCrossRef(rule_name, rule_name, node.position)
rule_ref.sem = rule_ref_SA


def textx_rule_body_SA(parser, node, children):
    if len(children) > 1:
        return Sequence(nodes=children[:])
    else:
        return children[0]
textx_rule_body.sem = textx_rule_body_SA


def sequence_SA(parser, node, children):
    if len(children) > 1:
        return Sequence(nodes=children[:])
    else:
        return children[0]
sequence.sem = sequence_SA


def choice_SA(parser, node, children):
    # If there is only one child reduce as
    # this ordered choice is unnecessary
    if len(children) > 1:
        return OrderedChoice(nodes=children[:])
    else:
        return children[0]
choice.sem = choice_SA


def expression_SA(parser, node, children):
    if len(children) > 1:
        if children[0] == '!':
            return Not(nodes=[children[1]])
        else:
            return And(nodes=[children[1]])
    else:
        return children[0]
expression.sem=expression_SA


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
    repeat_op = False
    suppress = False
    if len(children) > 1:
        # We can have repeat operator and/or suppression operator
        if len(children) > 2:
            repeat_op = children[1]
            suppress = True
        else:
            if children[1] == '-':
                suppress = True
            else:
                repeat_op = children[1]

        if repeat_op:
            if len(repeat_op) > 1:
                repeat_op, modifiers = repeat_op
            else:
                repeat_op = repeat_op[0]
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
                    raise TextXSyntaxError(
                        'Modifiers are not allowed for "?" operator at {}'
                        .format(text((line, col))), line, col)
                # Separator modifier
                if 'sep' in modifiers:
                    sep = modifiers['sep']
                    rule = Sequence(nodes=[expr,
                                    ZeroOrMore(nodes=[
                                            Sequence(nodes=[sep, expr])])])
                    if repeat_op == '*':
                        rule = Optional(nodes=[rule])

                # End of line termination modifier
                if 'eolterm' in modifiers:
                    rule.eolterm = True

    # Mark rule for suppression
    rule.suppress = suppress

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
    Create parser rule for assignments and register attribute types
    on metaclass.
    """
    attr_name = children[0]
    op = children[1]
    rhs_rule, modifiers = children[2]
    cls = parser._current_cls
    target_cls = None

    if parser.debug:
        parser.dprint("Processing assignment {}{}...".format(attr_name, op))

    if parser.debug:
        parser.dprint("Creating attribute {}:{}".format(cls.__name__,
                                                        attr_name))
        parser.dprint("Assignment operation = {}".format(op))

    if attr_name in cls._tx_attrs:
        # If attribute already exists in the metamodel it is
        # multiple assignment to the same attribute.

        # Cannot use operator ?= on multiple assignments
        if op == '?=':
            line, col = parser.pos_to_linecol(node.position)
            raise TextXSemanticError(
                'Cannot use "?=" operator on multiple'
                ' assignments for attribute "{}" at {}'
                .format(attr_name, (line, col)), line, col)

        cls_attr = cls._tx_attrs[attr_name]
        # Must be a many multiplicity.
        # OneOrMore is "stronger" constraint.
        if cls_attr.mult is not MULT_ONEORMORE:
            cls_attr.mult = MULT_ZEROORMORE
    else:
        cls_attr = parser.metamodel._new_cls_attr(cls, name=attr_name,
                                                  position=node.position)

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
        if cls_attr.mult is not MULT_ONEORMORE:
            cls_attr.mult = MULT_ZEROORMORE
    elif op == '?=':
        assignment_rule = Optional(
            nodes=[rhs_rule],
            rule_name='__asgn_optional', root=True)
        cls_attr.mult = MULT_OPTIONAL
        base_rule_name = 'BOOL'

        # ?= assigment should have default value of False.
        # so we shall mark it as such.
        cls_attr.bool_assignment = True

    else:
        assignment_rule = Sequence(
            nodes=[rhs_rule],
            rule_name='__asgn_plain', root=True)

    # Modifiers
    if modifiers:
        modifiers, position = modifiers
        # Sanity check. Modifiers do not make
        # sense for ?= and = operator at the moment.
        if op == '?=' or op == '=':
            line, col = parser.pos_to_linecol(position)
            raise TextXSyntaxError(
                'Modifiers are not allowed for "{}" operator at {}'
                .format(op, text((line, col))), line, col)

        # Separator modifier
        if 'sep' in modifiers:
            sep = modifiers['sep']
            assignment_rule = Sequence(
                nodes=[rhs_rule,
                       ZeroOrMore(nodes=[Sequence(nodes=[sep, rhs_rule])])],
                rule_name='__asgn_list', root=True)
            if op == "*=":
                assignment_rule.root = False
                assignment_rule = Optional(nodes=[assignment_rule],
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
        parser.dprint("Created attribute {}:{}[cls={}, cont={}, "
                      "ref={}, mult={}, pos={}]"
                      .format(cls.__name__, attr_name, cls_attr.cls.cls_name,
                              cls_attr.cont, cls_attr.ref, cls_attr.mult,
                              cls_attr.position))

    assignment_rule._attr_name = attr_name
    assignment_rule._exp_str = attr_name    # For nice error reporting
    return assignment_rule
assignment.sem = assignment_SA


def str_match_SA(parser, node, children):
    try:
        to_match = children[0]
    except:
        to_match = ''

    # Support for autokwd metamodel param.
    if parser.metamodel.autokwd:
        match = parser.keyword_regex.match(to_match)
        if match and match.span() == (0, len(to_match)):
            regex_match = RegExMatch(r'{}\b'.format(to_match),
                                     ignore_case=parser.metamodel.ignore_case,
                                     str_repr=to_match)
            regex_match.compile()
            return regex_match
    return StrMatch(to_match, ignore_case=parser.metamodel.ignore_case)
str_match.sem = str_match_SA


def re_match_SA(parser, node, children):
    try:
        to_match = children[0]
    except:
        to_match = ''
    regex = RegExMatch(to_match, ignore_case=parser.metamodel.ignore_case)
    try:
        regex.compile()
    except Exception as e:
        line, col = parser.pos_to_linecol(node[1].position)
        raise TextXSyntaxError(
            "{} at {}"
            .format(text(e), text((line, col))), line, col)
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


def integer_SA(parser, node, children):
    return int(node.value)
integer.sem = integer_SA


def string_value_SA(parser, node, children):
    return node.value.strip("\"'")
string_value.sem = string_value_SA


# Default actions
bracketed_sequence.sem = SemanticActionSingleChild()


# parser object cache. To speed up parser initialization (e.g. during imports)
textX_parsers = {}


def language_from_str(language_def, metamodel):
    """
    Constructs parser and initializes metamodel from language description
    given in textX language.

    Args:
        language_def (str): A language description in textX.
        metamodel (TextXMetaModel): A metamodel to initialize.

    Returns:
        Parser for the new language.
    """

    if metamodel.debug:
        metamodel.dprint("*** PARSING LANGUAGE DEFINITION ***")

    # Check the cache for already conctructed textX parser
    if metamodel.debug in textX_parsers:
        parser = textX_parsers[metamodel.debug]
    else:
        # Create parser for TextX descriptions from
        # the textX grammar specified in this module
        parser = ParserPython(textx_model, comment_def=comment,
                              ignore_case=False,
                              reduce_tree=False, debug=metamodel.debug)

        # Prepare regex used in keyword-like strmatch detection.
        # See str_match_SA
        flags = 0
        if metamodel.ignore_case:
            flags = re.IGNORECASE
        parser.keyword_regex = re.compile(r'[^\d\W]\w*', flags)

        # Cache it for subsequent calls
        textX_parsers[metamodel.debug] = parser

    # This is used during parser construction phase.
    # Metamodel is filled in. Classes are created based on grammar rules.
    parser.metamodel = metamodel

    # Builtin rules representing primitive types
    parser.root_rule_name = None

    # Parse language description with textX parser
    try:
        parser.parse(language_def)
    except NoMatch as e:
        line, col = parser.pos_to_linecol(e.position)
        raise TextXSyntaxError(text(e), line, col)

    # Construct new parser based on the given language description.
    lang_parser = parser.getASG()

    # Meta-model is constructed. Validate semantics of metamodel.
    parser.metamodel.validate()

    # Meta-model is constructed. Here we connect meta-model and language
    # parser for convenience.
    lang_parser.metamodel = parser.metamodel
    metamodel.parser = lang_parser

    if metamodel.debug:
        # Create dot file for debuging purposes
        PMDOTExporter().exportFile(
            lang_parser.parser_model,
            "{}_parser_model.dot".format(metamodel.rootcls.__name__))

    return lang_parser

