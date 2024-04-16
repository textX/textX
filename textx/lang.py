"""
Implementation of textX language in Arpeggio.

The idea for this language is shamelessly stolen from the Xtext language but
there are some differences in both syntax and semantics. To make things clear I
have named this language textX ;)

"""
import codecs
import re

from arpeggio import (
    EOF,
    And,
    Match,
    NoMatch,
    Not,
    OneOrMore,
    Optional,
    OrderedChoice,
    ParserPython,
    ParsingExpression,
    RegExMatch,
    Sequence,
    StrMatch,
    UnorderedGroup,
    ZeroOrMore,
    visit_parse_tree,
)
from arpeggio import RegExMatch as _
from arpeggio.export import PMDOTExporter

from textx.scoping.rrel import RRELVisitor, rrel_expression

from .const import (
    MULT_ONE,
    MULT_ONEORMORE,
    MULT_OPTIONAL,
    MULT_ZEROORMORE,
    RULE_ABSTRACT,
    RULE_COMMON,
    RULE_MATCH,
    mult_lt,
)
from .exceptions import TextXError, TextXSemanticError, TextXSyntaxError

# Interpreting backslash sequences.
# See https://stackoverflow.com/a/24519338/2024430
ESCAPE_SEQUENCE_RE = re.compile(
    r"""
    ( \\U........      # 8-digit hex escapes
    | \\u....          # 4-digit hex escapes
    | \\x..            # 2-digit hex escapes
    | \\[0-7]{1,3}     # Octal escapes
    | \\N\{[^}]+\}     # Unicode characters by name
    | \\[\\'"abfnrtv]  # Single-character escapes
    )""",
    re.UNICODE | re.VERBOSE,
)


def decode_escapes(s):
    def decode_match(match):
        return codecs.decode(match.group(0), "unicode-escape")

    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)


# textX grammar
def textx_model():
    return (ZeroOrMore(import_or_reference_stm), ZeroOrMore(textx_rule), EOF)


def import_or_reference_stm():
    return [import_stm, reference_stm]


def import_stm():
    return "import", grammar_to_import


def reference_stm():
    return ("reference", language_name, Optional(language_alias))


def language_alias():
    return "as", ident


def language_name():
    return _(r"(\w|-)+")


def grammar_to_import():
    return _(r"(\w|\.)+")


# Rules
def textx_rule():
    return rule_name, Optional(rule_params), ":", textx_rule_body, ";"


def rule_params():
    return "[", rule_param, ZeroOrMore(",", rule_param), "]"


def rule_param():
    return param_name, Optional("=", string_value)


def param_name():
    return ident


def textx_rule_body():
    return choice


def choice():
    return sequence, ZeroOrMore("|", sequence)


def sequence():
    return OneOrMore(repeatable_expr)


def repeatable_expr():
    return expression, Optional(repeat_operator), Optional("-")


def expression():
    return [
        assignment,
        (Optional(syntactic_predicate), [simple_match, rule_ref, bracketed_choice]),
    ]


def bracketed_choice():
    return "(", choice, ")"


def repeat_operator():
    return ["*", "?", "+", "#"], Optional(repeat_modifiers)


def repeat_modifiers():
    return "[", OneOrMore([simple_match, "eolterm"]), "]"


def syntactic_predicate():
    return ["!", "&"]


def simple_match():
    return [str_match, re_match]


# Assignment
def assignment():
    return attribute, assignment_op, assignment_rhs


def attribute():
    return ident


def assignment_op():
    return ["=", "*=", "+=", "?="]


def assignment_rhs():
    return [simple_match, reference], Optional(repeat_modifiers)


# References
def reference():
    return [rule_ref, obj_ref]


def rule_ref():
    return ident


# TODO: Remove "|" optional sep in version 4.0.
def obj_ref():
    return (
        "[",
        class_name,
        Optional([":", "|"], obj_ref_rule, Optional("|", rrel_expression)),
        "]",
    )


def rule_name():
    return ident


def obj_ref_rule():
    return ident


def class_name():
    return qualified_ident


def str_match():
    return string_value


def re_match():
    return _(r"/((?:(?:\\/)|[^/])*)/")


def ident():
    return _(r"\w+")


def qualified_ident():
    return _(r"\w+(\.\w+)?")


def integer():
    return _(r"[-+]?[0-9]+")


def string_value():
    return [_(r"'((\\')|[^'])*'"), _(r'"((\\")|[^"])*"')]


# Comments
def comment():
    return [comment_line, comment_block]


def comment_line():
    return _(r"//.*?$")


def comment_block():
    return _(r"/\*(.|\n)*?\*/")


# Special rules - primitive types
ID = _(r"[^\d\W]\w*\b", rule_name="ID", root=True)
BOOL = _(r"(True|true|False|false|0|1)\b", rule_name="BOOL", root=True)
INT = _(r"[-+]?[0-9]+", rule_name="INT", root=True)
FLOAT = _(
    r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?(?<=[\w\.])(?![\w\.])", "FLOAT", root=True
)
STRICTFLOAT = _(
    r"[+-]?(((\d+\.(\d*)?|\.\d+)([eE][+-]?\d+)?)|((\d+)([eE][+-]?\d+)))(?<=[\w\.])(?![\w\.])",
    "STRICTFLOAT",
    root=True,
)
STRING = _(r'("(\\"|[^"])*")|(\'(\\\'|[^\'])*\')', "STRING", root=True)
NUMBER = OrderedChoice(nodes=[STRICTFLOAT, INT], rule_name="NUMBER", root=True)
BASETYPE = OrderedChoice(
    nodes=[NUMBER, FLOAT, BOOL, ID, STRING], rule_name="BASETYPE", root=True
)

# A dummy rule for generic type. This rule should never be used for parsing.
OBJECT = _(r"", rule_name="OBJECT", root=True)

BASE_TYPE_RULES = {
    rule.rule_name: rule
    for rule in [ID, BOOL, INT, FLOAT, STRICTFLOAT, STRING, NUMBER, BASETYPE]
}
BASE_TYPE_NAMES = list(BASE_TYPE_RULES.keys())
ALL_TYPE_NAMES = BASE_TYPE_NAMES + ["OBJECT"]

PRIMITIVE_PYTHON_TYPES = [int, float, str, bool]

for regex in [ID, BOOL, INT, FLOAT, STRICTFLOAT, STRING]:
    regex.compile()


def python_type(textx_type_name):
    """Return Python type from the name of base textx type."""
    return {
        "ID": str,
        "BOOL": bool,
        "INT": int,
        "FLOAT": float,
        "STRICTFLOAT": float,
        "STRING": str,
        "NUMBER": float,
        "BASETYPE": str,
    }.get(textx_type_name, textx_type_name)


class RuleCrossRef:
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
        rrel_tree: the RREL tree defined for this reference
    """

    def __init__(self, rule_name, cls, position, rrel_tree):
        self.rule_name = rule_name
        self.cls = cls
        self.position = position
        self.suppress = False
        self.scope_provider = None
        if rrel_tree is not None:
            from textx.scoping.rrel import create_rrel_scope_provider

            self.scope_provider = create_rrel_scope_provider(rrel_tree)

    def __str__(self):
        return self.rule_name


class ClassCrossRef:
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


class TextXVisitor(RRELVisitor):
    def __init__(self, grammar_parser, metamodel):
        self.grammar_parser = grammar_parser
        self.metamodel = metamodel
        self.debug = metamodel.debug

        # Prepare regex used in keyword-like strmatch detection.
        # See visit_str_match
        flags = 0
        if metamodel.ignore_case:
            flags = re.IGNORECASE
        self.keyword_regex = re.compile(r"[^\d\W]\w*", flags)

        super().__init__()

    def visit_textx_model(self, node, children):
        if "Comment" in self.metamodel:
            comments_model = self.metamodel["Comment"]._tx_peg_rule
        else:
            comments_model = None

        root_rule = children[0]
        from .model import get_model_parser

        model_parser = get_model_parser(
            root_rule,
            comments_model,
            ignore_case=self.metamodel.ignore_case,
            skipws=self.metamodel.skipws,
            ws=self.metamodel.ws,
            autokwd=self.metamodel.autokwd,
            memoization=self.metamodel.memoization,
            debug=self.metamodel.debug,
            file=self.metamodel.file,
        )

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
                grammar_parser.dprint(f"Resolving rule: {rule}")

            if isinstance(rule, RuleCrossRef):
                rule_name = rule.rule_name
                suppress = rule.suppress
                if rule_name in model_parser.metamodel:
                    rule = model_parser.metamodel[rule_name]._tx_peg_rule
                    if isinstance(rule, RuleCrossRef):
                        rule = _resolve_rule(rule)
                        model_parser.metamodel[rule_name]._tx_peg_rule = rule
                    if suppress:
                        # Special case. Suppression on rule reference.
                        _tx_class = rule._tx_class
                        rule = Sequence(
                            nodes=[rule], rule_name=rule_name, suppress=suppress
                        )
                        rule._tx_class = _tx_class
                else:
                    line, col = grammar_parser.pos_to_linecol(rule.position)
                    raise TextXSemanticError(
                        f'Unexisting rule "{rule.rule_name}" at position {(line, col)}.',
                        line,
                        col,
                        filename=model_parser.metamodel.file_name,
                    )

            assert isinstance(rule, ParsingExpression), f"{type(rule)}:{str(rule)}"

            # Recurse into subrules, and resolve rules.
            for idx, child in enumerate(rule.nodes):
                if child not in resolved_rules:
                    child = _resolve_rule(child)
                    rule.nodes[idx] = child

            return rule

        # Two pass resolving
        for i in range(2):
            if grammar_parser.debug:
                grammar_parser.dprint(f"RESOLVING RULE CROSS-REFS - PASS {i + 1}")

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
                if cls._tx_type != RULE_COMMON:
                    cls._tx_type = RULE_COMMON
                    has_change[0] = True
                return

            rule = cls._tx_peg_rule

            # Check if this rule is abstract. Abstract are root rules which
            # haven't got any attributes and reference at least one non-match
            # rule.
            abstract = False
            if rule.rule_name and cls.__name__ != rule.rule_name:
                # Special case. Body of the rule is a single rule reference and
                # the referenced rule is not match rule.
                target_cls = metamodel[rule.rule_name]
                _determine_rule_type(target_cls)
                abstract = target_cls._tx_type != RULE_MATCH
            else:
                # Find at least one referenced rule that is not match rule by
                # going down the parser model and finding root rules.
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

            if abstract and cls._tx_type != RULE_ABSTRACT:
                cls._tx_type = RULE_ABSTRACT
                has_change[0] = True
                # Add inherited classes to this rule's meta-class
                if rule.rule_name and cls.__name__ != rule.rule_name:
                    if rule._tx_class not in cls._tx_inh_by:
                        cls._tx_inh_by.append(rule._tx_class)
                else:
                    # Recursively append all referenced classes.
                    def _add_reffered_classes(rule, inh_by, start=False):
                        if rule.root and not start:
                            _determine_rule_type(rule._tx_class)
                            if (
                                rule._tx_class._tx_type != RULE_MATCH
                                and rule._tx_class not in inh_by
                            ):
                                inh_by.append(rule._tx_class)
                                # stop after first added/found type
                                return True
                        else:
                            is_ordered_choice = isinstance(rule, OrderedChoice)
                            inh_added = False
                            for r in rule.nodes:
                                inh_added |= _add_reffered_classes(r, inh_by)
                                if inh_added and not is_ordered_choice:
                                    # If not ordered choice we should get out
                                    # early as the rest of the rule shouldn't
                                    # influence the inheritance hierarchy.
                                    break
                            return inh_added
                        return False

                    _add_reffered_classes(rule, cls._tx_inh_by, start=True)

        # Multi-pass rule type resolving to support circular rule references.
        # `has_change` is a list to support outer scope variable change in
        # Python 2.x
        has_change = [True]
        while has_change[0]:
            has_change[0] = False
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
                try:
                    cls = metamodel[cls.cls_name]
                except KeyError as e:
                    line, col = grammar_parser.pos_to_linecol(cls.position)
                    raise TextXSemanticError(
                        f'Unknown class/rule "{cls.cls_name}".',
                        line=line,
                        col=col,
                        filename=metamodel.file_name,
                    ) from e
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
                    if (
                        attr.cls.__name__ in BASE_TYPE_NAMES
                        or attr.cls._tx_type == RULE_MATCH
                    ):
                        attr.ref = False
                        attr.cont = True
                        attr.is_base_type = True
                    else:
                        attr.ref = True
                        attr.is_base_type = False

                    if grammar_parser.debug:
                        grammar_parser.dprint(
                            f"Resolved attribute {cls.__name__}:{attr.name}"
                            f"[cls={attr.cls.__name__}, cont={attr.cont}, "
                            f"ref={attr.ref}, mult={attr.mult}, pos={attr.position}]"
                        )

            return cls

        if grammar_parser.debug:
            grammar_parser.dprint("RESOLVING METACLASS REFS")

        for cls in model_parser.metamodel:
            _resolve_cls(cls)

    def visit_import_stm(self, node, children):
        self.metamodel._new_import(children[0])

    def visit_reference_stm(self, node, children):
        if len(children) > 1:
            language_name, language_alias = children
        else:
            language_name, language_alias = children[0], children[0]

        self.metamodel.referenced_languages[language_alias] = language_name

    def visit_grammar_to_import(self, node, children):
        return str(node)

    def visit_textx_rule(self, node, children):
        if len(children) > 2:
            rule_name, rule_params, root_rule = children
        else:
            rule_name, root_rule = children
            rule_params = {}

        if root_rule.rule_name.startswith("__asgn") or (
            isinstance(root_rule, (Match, RuleCrossRef)) and rule_params
        ):
            # If it is assignment node it must be kept because it could be
            # e.g. single assignment in the rule.
            # Also, handle a special case where rule consists only of a single
            # match or single rule reference and there are rule modifiers
            # defined.
            root_rule = Sequence(
                nodes=[root_rule], rule_name=rule_name, root=True, **rule_params
            )
        else:
            if not isinstance(root_rule, RuleCrossRef):
                # Promote rule node to root node.
                root_rule.rule_name = rule_name
                root_rule.root = True
                for param in rule_params:
                    setattr(root_rule, param, rule_params[param])

        # Connect meta-class and the PEG rule
        cls = self.metamodel[rule_name]
        cls._tx_peg_rule = root_rule
        root_rule._tx_class = cls

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
                if isinstance(rule, OneOrMore):
                    mult = MULT_ONEORMORE
                elif isinstance(rule, ZeroOrMore) and mult != MULT_ONEORMORE:
                    mult = MULT_ZEROORMORE

                if rule.rule_name.startswith("__asgn"):
                    cls_attr = cls._tx_attrs[rule._attr_name]
                    if mult in [MULT_ZEROORMORE, MULT_ONEORMORE]:
                        if rule.rule_name == "__asgn_optional":
                            raise TextXSemanticError(
                                "Can't use bool assignment "
                                f'inside repetition in rule "{rule_name}" '
                                f'at {self.grammar_parser.pos_to_linecol(node.position)}.'
                            )
                        if mult_lt(cls_attr.mult, mult):
                            cls_attr.mult = mult
                    # If multiplicity is not "many" still we can have
                    # "many" multiplicity if same attribute has been
                    # assigned multiple times in the same OrderedChoice
                    # branch.
                    elif rule._attr_name in oc_branch_set:
                        cls_attr.mult = MULT_ONEORMORE
                    else:
                        # Keep track of assignments in the current OC
                        # branch.
                        oc_branch_set.add(rule._attr_name)

                if rule is root_rule or not rule.root:
                    for n in rule.nodes:
                        _update_attr_multiplicities(n, oc_branch_set, mult)

        _update_attr_multiplicities(root_rule, set())

        return root_rule

    def visit_rule_name(self, node, children):
        rule_name = str(node)

        if self.debug:
            self.dprint(f"Creating class: {rule_name}")

        # If a class is given by the user use it. Else, create new class.
        if self.metamodel.user_classes_provider is not None:
            cls = self.metamodel.user_classes_provider(rule_name)
            if cls is not None:
                self.metamodel.user_classes[rule_name] = cls
        else:
            cls = self.metamodel.user_classes.get(rule_name)

        if cls is not None:
            if rule_name in self.metamodel._used_rule_names_for_user_classes:
                raise TextXSemanticError(
                    "redefined imported rule"
                    + f" {rule_name}"
                    + " cannot be replaced by a user class"
                )
            self.metamodel._used_rule_names_for_user_classes.add(rule_name)

            # Initialize special attributes
            self.metamodel._init_class(cls, None, node.position, external_attributes=True)
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
        for name, value in children:
            if name not in ["skipws", "ws", "split"]:
                raise TextXSyntaxError(
                    f'Invalid rule param "{name}" '
                    f'at {self.grammar_parser.pos_to_linecol(node.position)}.'
                )

            if name == "split" and not isinstance(value, str):
                raise TextXError("param split requires a string parameter")
            if name == "split" and len(value) == 0:
                raise TextXError("param split requires a non-empty string parameter")
            if name == "ws" and "\\" in value:
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
            if param_name.startswith("no"):
                param_name = param_name[2:]
                param_value = False

        if self.debug:
            self.dprint(f"TextX rule param: {param_name}, {param_value}")

        return (param_name, param_value)

    def visit_rule_ref(self, node, children):
        rule_name = str(node)
        # Here a name of the meta-class (rule) is expected but to support
        # forward referencing we are postponing resolving to second_pass.
        return RuleCrossRef(rule_name, rule_name, node.position, None)

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
        if children[0] == "!":
            return Not(nodes=[children[1]])
        else:
            return And(nodes=[children[1]])

    def visit_repeat_modifiers(self, node, children):
        modifiers = {}
        for modifier in children:
            if isinstance(modifier, Match):
                # Separator
                modifier.rule_name = "sep"
                modifiers["sep"] = modifier
            elif isinstance(modifier, tuple):
                modifiers["multiplicity"] = modifier
            else:
                modifiers["eolterm"] = True
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
                if children[1] == "-":
                    suppress = True
                else:
                    repeat_op = children[1]

            if repeat_op:
                if len(repeat_op) > 1:
                    repeat_op, modifiers = repeat_op
                else:
                    repeat_op = repeat_op[0]
                    modifiers = None

                if repeat_op == "?":
                    rule = Optional(nodes=[expr])
                elif repeat_op == "*":
                    rule = ZeroOrMore(nodes=[expr])
                elif repeat_op == "+":
                    rule = OneOrMore(nodes=[expr])
                else:
                    rule = UnorderedGroup(nodes=expr.nodes)

                if modifiers:
                    modifiers, position = modifiers
                    # Sanity check. Modifiers do not make
                    # sense for ? operator at the moment.
                    if repeat_op == "?":
                        line, col = self.grammar_parser.pos_to_linecol(position)
                        raise TextXSyntaxError(
                            "Modifiers are not allowed "
                            f'for "?" operator at {(line, col)}',
                            line,
                            col,
                        )

                    # Separator modifier
                    rule.sep = modifiers.get("sep", None)

                    # End of line termination modifier
                    if "eolterm" in modifiers:
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
            self.dprint(f"Processing assignment {attr_name}{op}...")

        if self.debug:
            self.dprint(f"Creating attribute {cls.__name__}:{attr_name}")
            self.dprint(f"Assignment operation = {op}")

        if attr_name in cls._tx_attrs:
            # If attribute already exists in the metamodel it is
            # multiple assignment to the same attribute.

            # Cannot use operator ?= on multiple assignments
            if op == "?=":
                line, col = self.grammar_parser.pos_to_linecol(node.position)
                raise TextXSemanticError(
                    'Cannot use "?=" operator on multiple'
                    f' assignments for attribute "{attr_name}" at {(line, col)}',
                    line,
                    col,
                )

            cls_attr = cls._tx_attrs[attr_name]
        else:
            cls_attr = self.metamodel._new_cls_attr(
                cls, name=attr_name, position=node.position
            )

        # Keep track of metaclass references and containments
        if isinstance(rhs_rule, tuple) and rhs_rule[0] == "obj_ref":
            cls_attr.cont = False
            cls_attr.ref = True
            # Override rhs by its PEG rule for further processing
            rhs_rule = rhs_rule[1]
            # store RREL related information
            cls_attr.scope_provider = rhs_rule.scope_provider
            cls_attr.match_rule_name = rhs_rule.rule_name
            # Target class is not the same as target rule
            target_cls = rhs_rule.cls

        base_rule_name = rhs_rule.rule_name
        if op == "+=":
            assignment_rule = OneOrMore(
                nodes=[rhs_rule], rule_name="__asgn_oneormore", root=True
            )
            cls_attr.mult = MULT_ONEORMORE
        elif op == "*=":
            assignment_rule = ZeroOrMore(
                nodes=[rhs_rule], rule_name="__asgn_zeroormore", root=True
            )
            if cls_attr.mult is not MULT_ONEORMORE:
                cls_attr.mult = MULT_ZEROORMORE
        elif op == "?=":
            assignment_rule = Optional(
                nodes=[rhs_rule], rule_name="__asgn_optional", root=True
            )
            cls_attr.mult = MULT_OPTIONAL
            base_rule_name = "BOOL"

            # ?= assignment should have default value of False.
            # so we shall mark it as such.
            cls_attr.bool_assignment = True

        else:
            assignment_rule = Sequence(
                nodes=[rhs_rule], rule_name="__asgn_plain", root=True
            )

        # Modifiers
        if modifiers:
            modifiers, position = modifiers
            # Sanity check. Modifiers do not make
            # sense for ?= and = operator at the moment.
            if op == "?=" or op == "=":
                line, col = self.grammar_parser.pos_to_linecol(position)
                raise TextXSyntaxError(
                    f'Modifiers are not allowed for "{op}" operator at {(line, col)}',
                    line,
                    col,
                    filename=self.metamodel.file_name,
                )

            # Separator modifier
            assignment_rule.sep = modifiers.get("sep", None)

            # End of line termination modifier
            if "eolterm" in modifiers:
                assignment_rule.eolterm = True

        if target_cls:
            attr_type = target_cls
        else:
            # Use STRING as default attr class
            attr_type = base_rule_name if base_rule_name else "STRING"
        if not cls_attr.cls:
            cls_attr.cls = ClassCrossRef(cls_name=attr_type, position=node.position)
        else:
            # cls cross ref might already be set in case of multiple assignment
            # to the same attribute. If types are not the same we shall use
            # OBJECT as generic type.
            if cls_attr.cls.cls_name != attr_type:
                cls_attr.cls.cls_name = "OBJECT"

        if self.debug:
            self.dprint(
                f"Created attribute {cls.__name__}:{attr_name}"
                f"[cls={cls_attr.cls.cls_name}, cont={cls_attr.cont}, "
                f"ref={cls_attr.ref}, mult={cls_attr.mult}, pos={cls_attr.position}]"
            )

        assignment_rule._attr_name = attr_name
        assignment_rule._exp_str = attr_name  # For nice error reporting
        return assignment_rule

    def visit_str_match(self, node, children):
        try:
            to_match = children[0][1:-1]
            if "\\" in to_match:
                to_match = decode_escapes(to_match)

        except IndexError:
            to_match = ""

        # Support for autokwd metamodel param.
        if self.metamodel.autokwd:
            match = self.keyword_regex.match(to_match)
            if match and match.span() == (0, len(to_match)):
                regex_match = RegExMatch(
                    rf"{to_match}\b",
                    ignore_case=self.metamodel.ignore_case,
                    str_repr=to_match,
                )
                regex_match.compile()
                return regex_match
        return StrMatch(to_match, ignore_case=self.metamodel.ignore_case)

    def visit_re_match(self, node, children):
        to_match = node.extra_info.group(1)
        # print("**** visit_re_match, to_match == '{}'".format(to_match))
        regex = RegExMatch(to_match, ignore_case=self.metamodel.ignore_case)
        try:
            regex.compile()
        except Exception as e:
            line, col = self.grammar_parser.pos_to_linecol(node[1].position)
            raise TextXSyntaxError(str(e), line, col) from e
        return regex

    def visit_obj_ref(self, node, children):
        # A reference to some other class instance will be the value of
        # its "name" attribute.
        class_name = children[0]
        rrel_tree = None
        if class_name in BASE_TYPE_NAMES:
            line, col = self.grammar_parser.pos_to_linecol(node.position)
            raise TextXSemanticError(
                f"Primitive type instances can not be referenced at {(line, col)}.",
                line,
                col,
            )
        if len(children) > 1:
            rule_name = children[2]
            if len(children) > 3:
                rrel_tree = children[3]
        else:
            # Default rule for matching obj cross-refs
            rule_name = "ID"
        return ("obj_ref", RuleCrossRef(rule_name, class_name, node.position, rrel_tree))

    def visit_integer(self, node, children):
        return int(node.value)

    def visit_string_value(self, node, children):
        return node.value[1:-1]

    def bracketed_choice(self, node, children):
        return children[0]


# parser object cache. To speed up parser initialization (e.g. during imports)
textX_parsers = {}


def language_from_str(language_def, metamodel, file_name):
    """
    Constructs parser and initializes metamodel from language description
    given in textX language.

    Args:
        language_def (str): A language description in textX.
        metamodel (TextXMetaModel): A metamodel to initialize.

    Returns:
        Parser for the new language.
    """

    if not isinstance(language_def, str):
        raise TextXError("textX accepts only strings.")

    if metamodel.debug:
        metamodel.dprint("*** PARSING LANGUAGE DEFINITION ***")

    # Check the cache for already conctructed textX parser
    if metamodel.debug in textX_parsers:
        parser = textX_parsers[metamodel.debug]
    else:
        # Create parser for TextX grammars using
        # the arpeggio grammar specified in this module
        parser = ParserPython(
            textx_model,
            comment_def=comment,
            ignore_case=False,
            reduce_tree=False,
            memoization=metamodel.memoization,
            debug=metamodel.debug,
            file=metamodel.file,
        )

        # Cache it for subsequent calls
        textX_parsers[metamodel.debug] = parser

    # Parse language description with textX parser
    try:
        parse_tree = parser.parse(language_def, file_name)
    except NoMatch as e:
        e.eval_attrs()
        raise TextXSyntaxError(
            e.message, e.line, e.col, filename=e.parser.file_name, context=e.context
        ) from e

    # Construct new parser and meta-model based on the given language
    # description.
    lang_parser = visit_parse_tree(parse_tree, TextXVisitor(parser, metamodel))

    # Meta-model is constructed. Validate its semantics.
    metamodel.validate()

    # Here we connect meta-model and language parser for convenience.
    lang_parser.metamodel = metamodel
    metamodel._parser_blueprint = lang_parser

    if metamodel.debug:
        # Create dot file for debugging purposes
        PMDOTExporter().exportFile(
            lang_parser.parser_model,
            f"{metamodel.rootcls.__name__}_parser_model.dot",
        )

    return lang_parser
