#######################################################################
# Name: textx.py
# Purpose: Implementation of textX language in Arpeggio.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014-2016 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#
# The idea for this language is shamelessly stolen from the Xtext language
# but there are some differences in both syntax and semantics.
# To make things clear I have named this language textX ;)
#######################################################################

from __future__ import unicode_literals
import re
from arpeggio import StrMatch, Optional, ZeroOrMore, OneOrMore, Sequence,\
    OrderedChoice, UnorderedGroup, Not, And, RegExMatch, Match, NoMatch, EOF, \
    ParsingExpression, ParserPython, PTNodeVisitor, visit_parse_tree
from arpeggio.export import PMDOTExporter
from arpeggio import RegExMatch as _

from .exceptions import TextXSyntaxError, TextXSemanticError
from .const import MULT_ONE, MULT_ZEROORMORE, MULT_ONEORMORE, \
    MULT_OPTIONAL, RULE_COMMON, RULE_MATCH, RULE_ABSTRACT, mult_lt

import sys
if sys.version < '3':
    text = unicode
else:
    text = str


# textX grammar
def textx_model():          return ZeroOrMore(import_stm), ZeroOrMore(textx_rule), EOF

def import_stm():           return 'import', grammar_to_import
def grammar_to_import():    return _(r'(\w|\.)+')

# Rules
def textx_rule():           return rule_name, Optional(rule_params), ":", textx_rule_body, ";"
def rule_params():          return '[', rule_param, ZeroOrMore(',', rule_param), ']'
def rule_param():           return param_name, Optional('=', string_value)
def param_name():           return ident
def textx_rule_body():      return choice

def choice():               return sequence, ZeroOrMore("|", sequence)
def sequence():             return OneOrMore(repeatable_expr)
def repeatable_expr():      return expression, Optional(repeat_operator), Optional('-')
def expression():           return [assignment, (Optional(syntactic_predicate),
                                                 [simple_match, rule_ref,
                                                  bracketed_choice])]
def bracketed_choice():     return '(', choice, ')'
def repeat_operator():      return ['*', '?', '+', '#'], Optional(repeat_modifiers)
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

# A dummy rule for generic type. This rule should never be used for parsing.
OBJECT = _(r'', rule_name='OBJECT', root=True)

BASE_TYPE_RULES = {rule.rule_name: rule
                   for rule in [ID, BOOL, INT, FLOAT,
                                STRING, NUMBER, BASETYPE]}
BASE_TYPE_NAMES = list(BASE_TYPE_RULES.keys())
ALL_TYPE_NAMES = BASE_TYPE_NAMES + ['OBJECT']

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


class TextXVisitor(PTNodeVisitor):

    def __init__(self, grammar_parser, metamodel):
        self.grammar_parser = grammar_parser
        self.metamodel = metamodel
        self.debug = metamodel.debug

        # Prepare regex used in keyword-like strmatch detection.
        # See visit_str_match
        flags = 0
        if metamodel.ignore_case:
            flags = re.IGNORECASE
        self.keyword_regex = re.compile(r'[^\d\W]\w*', flags)

        super(TextXVisitor, self).__init__()

    def visit_textx_model(self, node, children):

        if 'Comment' in self.metamodel:
            comments_model = self.metamodel['Comment']._tx_peg_rule
        else:
            comments_model = None

        root_rule = children[0]
        from .model import get_model_parser
        model_parser = get_model_parser(root_rule, comments_model,
                                        ignore_case=self.metamodel.ignore_case,
                                        skipws=self.metamodel.skipws,
                                        ws=self.metamodel.ws,
                                        autokwd=self.metamodel.autokwd,
                                        memoization=self.metamodel.memoization,
                                        debug=self.metamodel.debug)

        model_parser.metamodel = self.metamodel

        return model_parser

    def second_textx_model(self, model_parser):
        """Cross reference resolving for parser model."""

        if self.grammar_parser.debug:
            self.grammar_parser.dprint("RESOLVING MODEL PARSER: second_pass")

        self._resolve_rule_refs(self.grammar_parser, model_parser)
        self._determine_rule_types(model_parser.metamodel)
        self._resolve_cls_refs(self.grammar_parser, model_parser)

        return model_parser

    def _resolve_rule_refs(self, grammar_parser, model_parser):
        """Resolves parser ParsingExpression crossrefs."""

        def _resolve_rule(rule):
            """
            Recursively resolve peg rule references.

            Args:
                rule(ParsingExpression or RuleCrossRef)
            """
            if not isinstance(rule, RuleCrossRef) and rule in resolved_rules:
                return rule
            resolved_rules.add(rule)

            if grammar_parser.debug:
                grammar_parser.dprint("Resolving rule: {}".format(rule))

            if type(rule) is RuleCrossRef:
                rule_name = rule.rule_name
                suppress = rule.suppress
                if rule_name in model_parser.metamodel:
                    rule = model_parser.metamodel[rule_name]._tx_peg_rule
                    if type(rule) is RuleCrossRef:
                        rule = _resolve_rule(rule)
                        model_parser.metamodel[rule_name]._tx_peg_rule = rule
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

            # Recurse into subrules, and resolve rules.
            for idx, child in enumerate(rule.nodes):
                if child not in resolved_rules:
                    child = _resolve_rule(child)
                    rule.nodes[idx] = child

            return rule

        # Two pass resolving
        for i in range(2):
            if grammar_parser.debug:
                grammar_parser.dprint("RESOLVING RULE CROSS-REFS - PASS {}"
                                      .format(i + 1))

            resolved_rules = set()
            _resolve_rule(model_parser.parser_model)

            # Resolve rules of all meta-classes to handle unreferenced
            # rules also.
            for cls in model_parser.metamodel:
                cls._tx_peg_rule = _resolve_rule(cls._tx_peg_rule)

    def _determine_rule_types(self, metamodel):
        """Determine textX rule/metaclass types"""

        def _determine_rule_type(cls):
            """
            Determine rule type (abstract, match, common) and inherited
            classes.
            """

            if cls in resolved_classes:
                return
            resolved_classes.add(cls)

            # If there are attributes collected than this is a common
            # rule
            if len(cls._tx_attrs) > 0:
                cls._tx_type = RULE_COMMON
                return

            rule = cls._tx_peg_rule

            # Check if this rule is abstract
            # Abstract are root rules which haven't got any attributes
            # and reference at least one non-match rule.
            abstract = False
            if rule.rule_name and cls.__name__ != rule.rule_name:
                # Special case. Body of the rule is a single rule
                # reference and the referenced rule is not match rule.
                target_cls = metamodel[rule.rule_name]
                _determine_rule_type(target_cls)
                abstract = target_cls._tx_type != RULE_MATCH
            else:
                # Find at leat one referenced rule that is not match
                # rule by going down the parser
                # model and finding root rules.
                def _has_nonmatch_ref(rule):
                    for r in rule.nodes:
                        if r.root:
                            _determine_rule_type(r._tx_class)
                            result = r._tx_class._tx_type != RULE_MATCH
                        else:
                            result = _has_nonmatch_ref(r)
                        if result:
                            return True
                abstract = _has_nonmatch_ref(rule)

            if abstract:
                cls._tx_type = RULE_ABSTRACT
                # Add inherited classes to this rule's meta-class
                if rule.rule_name and cls.__name__ != rule.rule_name:
                    if rule._tx_class not in cls._tx_inh_by:
                        cls._tx_inh_by.append(rule._tx_class)
                else:
                    # Recursivelly append all referenced classes.
                    def _add_reffered_classes(rule, inh_by):
                        for r in rule.nodes:
                            if r.root:
                                if hasattr(r, '_tx_class'):
                                    _determine_rule_type(r._tx_class)
                                    if r._tx_class._tx_type != RULE_MATCH and\
                                            r._tx_class not in inh_by:
                                        inh_by.append(r._tx_class)
                            else:
                                _add_reffered_classes(r, inh_by)
                    _add_reffered_classes(rule, cls._tx_inh_by)

        resolved_classes = set()
        for cls in metamodel:
            _determine_rule_type(cls)

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

                # If this is not abstract class than it must be common or
                # match. Resolve referred classes.
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

    def visit_import_stm(self, node, children):
        self.metamodel._new_import(children[0])

    def visit_grammar_to_import(self, node, children):
        return text(node)

    def visit_textx_rule(self, node, children):
        if len(children) > 2:
            rule_name, rule_params, rule = children
        else:
            rule_name, rule = children
            rule_params = {}

        if rule.rule_name.startswith('__asgn') or\
                ((isinstance(rule, Match) or isinstance(rule, RuleCrossRef))
                 and rule_params):
            # If it is assignment node it must be kept because it could be
            # e.g. single assignment in the rule.
            # Also, handle a special case where rule consists only of a single
            # match or single rule reference and there are rule modifiers
            # defined.
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
        cls = self.metamodel[rule_name]
        cls._tx_peg_rule = rule
        rule._tx_class = cls

        # Update end position for this rule.
        cls._tx_position_end = node.position_end

        # Update multiplicities of attributes based on their parent
        # expressions.
        def _update_attr_multiplicities(rule, oc_branch_set, mult=MULT_ONE):

            if isinstance(rule, RuleCrossRef):
                return

            if isinstance(rule, OrderedChoice):
                for on in rule.nodes:
                    oc_branch_set = set()
                    _update_attr_multiplicities(on, oc_branch_set, mult)
            else:

                for n in [x for x in rule.nodes
                          if not isinstance(x, RuleCrossRef)]:

                    m = mult
                    if isinstance(n, OneOrMore):
                        m = MULT_ONEORMORE
                    elif isinstance(n, ZeroOrMore):
                        if m != MULT_ONEORMORE:
                            m = MULT_ZEROORMORE

                    if n.rule_name.startswith('__asgn'):
                        cls_attr = cls._tx_attrs[n._attr_name]
                        if mult in [MULT_ZEROORMORE, MULT_ONEORMORE]:
                            if mult_lt(cls_attr.mult, m):
                                cls_attr.mult = m
                        # If multiplicity is not "many" still we can have
                        # "many" multiplicity if same attribute has been
                        # assigned multiple times in the same OrderedChoice
                        # branch.
                        elif n._attr_name in oc_branch_set:
                            cls_attr.mult = MULT_ONEORMORE
                        else:
                            # Keep track of assignments in the current OC
                            # branch.
                            oc_branch_set.add(n._attr_name)

                    elif not n.root:
                        _update_attr_multiplicities(n, oc_branch_set, m)

        _update_attr_multiplicities(rule, set())

        return rule

    def visit_rule_name(self, node, children):
        rule_name = str(node)

        if self.debug:
            self.dprint("Creating class: {}".format(rule_name))

        # If a class is given by the user use it. Else, create new class.
        if rule_name in self.metamodel.user_classes:

            cls = self.metamodel.user_classes[rule_name]

            # Initialize special attributes
            self.metamodel._init_class(cls, None, node.position)
        else:
            # Create class to collect attributes. At this time PEG rule
            # is not known.
            cls = self.metamodel._new_class(rule_name, None, node.position)

        self._current_cls = cls

        # First class will be the root of the meta-model
        if not self.metamodel.rootcls:
            self.metamodel.rootcls = cls

        return rule_name

    def visit_rule_params(self, node, children):
        params = {}
        for name, value in children[0].items():
            if name not in ['skipws', 'ws']:
                raise TextXSyntaxError(
                    'Invalid rule param "{}" at {}.'
                    .format(name,
                            self.grammar_parser.pos_to_linecol(node.position)))

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

    def visit_rule_param(self, node, children):
        if len(children) > 1:
            param_name, param_value = children
        else:
            param_name = children[0]
            param_value = True
            if param_name.startswith('no'):
                param_name = param_name[2:]
                param_value = False

        if self.debug:
            self.dprint("TextX rule param: {}, {}".format(param_name,
                                                          param_value))

        return {param_name: param_value}

    def visit_rule_ref(self, node, children):
        rule_name = text(node)
        # Here a name of the meta-class (rule) is expected but to support
        # forward referencing we are postponing resolving to second_pass.
        return RuleCrossRef(rule_name, rule_name, node.position)

    def visit_textx_rule_body(self, node, children):
        if len(children) == 1:
            return children[0]
        return OrderedChoice(nodes=children[:])

    def visit_sequence(self, node, children):
        if len(children) == 1:
            return children[0]
        return Sequence(nodes=children[:])

    def visit_choice(self, node, children):
        # If there is only one child reduce as
        # this ordered choice is unnecessary
        if len(children) == 1:
            return children[0]
        return OrderedChoice(nodes=children[:])

    def visit_expression(self, node, children):
        if len(children) == 1:
            return children[0]
        if children[0] == '!':
            return Not(nodes=[children[1]])
        else:
            return And(nodes=[children[1]])

    def visit_repeat_modifiers(self, node, children):
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

    def visit_repeat_operator(self, node, children):
        return children

    def visit_repeatable_expr(self, node, children):
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
                elif repeat_op == '+':
                    rule = OneOrMore(nodes=[expr])
                else:
                    rule = UnorderedGroup(nodes=expr.nodes)

                if modifiers:
                    modifiers, position = modifiers
                    # Sanity check. Modifiers do not make
                    # sense for ? operator at the moment.
                    if repeat_op == '?':
                        line, col = \
                            self.grammar_parser.pos_to_linecol(position)
                        raise TextXSyntaxError(
                            'Modifiers are not allowed for "?" operator at {}'
                            .format(text((line, col))), line, col)

                    # Separator modifier
                    rule.sep = modifiers.get('sep', None)

                    # End of line termination modifier
                    if 'eolterm' in modifiers:
                        rule.eolterm = True

        # Mark rule for suppression
        rule.suppress = suppress

        return rule

    def visit_assignment_rhs(self, node, children):
        rule = children[0]
        modifiers = None
        if len(children) > 1:
            modifiers = children[1]

        # At this level we do not know the type of assignment (=, +=, *=)
        # and we do not have access to the PEG rule so postpone
        # rule modification for assignment semantic action.
        return (rule, modifiers)

    def visit_assignment(self, node, children):
        """
        Create parser rule for assignments and register attribute types
        on metaclass.
        """
        attr_name = children[0]
        op = children[1]
        rhs_rule, modifiers = children[2]
        cls = self._current_cls
        target_cls = None

        if self.debug:
            self.dprint("Processing assignment {}{}..."
                        .format(attr_name, op))

        if self.debug:
            self.dprint("Creating attribute {}:{}".format(cls.__name__,
                                                          attr_name))
            self.dprint("Assignment operation = {}".format(op))

        if attr_name in cls._tx_attrs:
            # If attribute already exists in the metamodel it is
            # multiple assignment to the same attribute.

            # Cannot use operator ?= on multiple assignments
            if op == '?=':
                line, col = self.grammar_parser.pos_to_linecol(node.position)
                raise TextXSemanticError(
                    'Cannot use "?=" operator on multiple'
                    ' assignments for attribute "{}" at {}'
                    .format(attr_name, (line, col)), line, col)

            cls_attr = cls._tx_attrs[attr_name]
        else:
            cls_attr = self.metamodel._new_cls_attr(cls, name=attr_name,
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
                line, col = self.grammar_parser.pos_to_linecol(position)
                raise TextXSyntaxError(
                    'Modifiers are not allowed for "{}" operator at {}'
                    .format(op, text((line, col))), line, col)

            # Separator modifier
            assignment_rule.sep = modifiers.get('sep', None)

            # End of line termination modifier
            if 'eolterm' in modifiers:
                assignment_rule.eolterm = True

        if target_cls:
            attr_type = target_cls
        else:
            # Use STRING as default attr class
            attr_type = base_rule_name if base_rule_name else 'STRING'
        if not cls_attr.cls:
            cls_attr.cls = ClassCrossRef(cls_name=attr_type,
                                         position=node.position)
        else:
            # cls cross ref might already be set in case of multiple assignment
            # to the same attribute. If types are not the same we shall use
            # OBJECT as generic type.
            if cls_attr.cls.cls_name != attr_type:
                cls_attr.cls.cls_name = 'OBJECT'

        if self.debug:
            self.dprint("Created attribute {}:{}[cls={}, cont={}, "
                        "ref={}, mult={}, pos={}]"
                        .format(cls.__name__, attr_name, cls_attr.cls.cls_name,
                                cls_attr.cont, cls_attr.ref, cls_attr.mult,
                                cls_attr.position))

        assignment_rule._attr_name = attr_name
        assignment_rule._exp_str = attr_name    # For nice error reporting
        return assignment_rule

    def visit_str_match(self, node, children):
        try:
            to_match = children[0]
        except:
            to_match = ''

        # Support for autokwd metamodel param.
        if self.metamodel.autokwd:
            match = self.keyword_regex.match(to_match)
            if match and match.span() == (0, len(to_match)):
                regex_match = RegExMatch(
                    r'{}\b'.format(to_match),
                    ignore_case=self.metamodel.ignore_case,
                    str_repr=to_match)
                regex_match.compile()
                return regex_match
        return StrMatch(to_match, ignore_case=self.metamodel.ignore_case)

    def visit_re_match(self, node, children):
        try:
            to_match = children[0]
        except:
            to_match = ''
        regex = RegExMatch(to_match,
                           ignore_case=self.metamodel.ignore_case)
        try:
            regex.compile()
        except Exception as e:
            line, col = self.grammar_parser.pos_to_linecol(node[1].position)
            raise TextXSyntaxError(
                "{} at {}"
                .format(text(e), text((line, col))), line, col)
        return regex

    def visit_obj_ref(self, node, children):
        # A reference to some other class instance will be the value of
        # its "name" attribute.
        class_name = children[0]
        if class_name in BASE_TYPE_NAMES:
            line, col = self.grammar_parser.pos_to_linecol(node.position)
            raise TextXSemanticError(
                'Primitive type instances can not be referenced at {}.'
                .format((line, col)), line, col)
        if len(children) > 1:
            rule_name = children[1]
        else:
            # Default rule for matching obj cross-refs
            rule_name = 'ID'
        return ("obj_ref", RuleCrossRef(rule_name, class_name, node.position))

    def visit_integer(self, node, children):
        return int(node.value)

    def visit_string_value(self, node, children):
        return node.value.strip("\"'")

    def bracketed_choice(self, node, children):
        return children[0]


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
        # Create parser for TextX grammars using
        # the arpeggio grammar specified in this module
        parser = ParserPython(textx_model, comment_def=comment,
                              ignore_case=False,
                              reduce_tree=False,
                              memoization=metamodel.memoization,
                              debug=metamodel.debug)

        # Cache it for subsequent calls
        textX_parsers[metamodel.debug] = parser

    # Parse language description with textX parser
    try:
        parse_tree = parser.parse(language_def)
    except NoMatch as e:
        line, col = parser.pos_to_linecol(e.position)
        raise TextXSyntaxError(text(e), line, col)

    # Construct new parser and meta-model based on the given language
    # description.
    lang_parser = visit_parse_tree(parse_tree,
                                   TextXVisitor(parser, metamodel))

    # Meta-model is constructed. Validate its semantics.
    metamodel.validate()

    # Here we connect meta-model and language parser for convenience.
    lang_parser.metamodel = metamodel
    metamodel.parser = lang_parser

    if metamodel.debug:
        # Create dot file for debuging purposes
        PMDOTExporter().exportFile(
            lang_parser.parser_model,
            "{}_parser_model.dot".format(metamodel.rootcls.__name__))

    return lang_parser
