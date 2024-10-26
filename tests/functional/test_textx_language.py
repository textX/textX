import pytest

from textx import TextXSyntaxError, metamodel_from_str
from textx.const import RULE_ABSTRACT, RULE_COMMON, RULE_MATCH
from textx.lang import ALL_TYPE_NAMES


def test_common_rule():
    grammar = """
    Model: a = 'something';
    """
    meta = metamodel_from_str(grammar)
    assert meta

    model = meta.model_from_str("something")
    assert model
    assert model.__class__.__name__ == "Model"
    assert model.a == "something"


def test_abstract_rule():
    grammar = """
    Model: 'start' attr=Rule;
    Rule: Rule1|Rule2|Rule3;
    Rule1: RuleA|RuleB;
    RuleA: a=INT;
    RuleB: a=STRING;
    Rule2: b=STRING;
    Rule3: c=ID;
    """
    meta = metamodel_from_str(grammar)
    assert meta
    assert set([x.__name__ for x in meta]) == set(
        ["Model", "Rule", "RuleA", "RuleB", "Rule1", "Rule2", "Rule3"]
    ).union(set(ALL_TYPE_NAMES))
    assert meta["Rule"]._tx_type is RULE_ABSTRACT
    assert meta["Rule1"]._tx_type is RULE_ABSTRACT

    model = meta.model_from_str("start 34")
    assert model
    assert model.attr
    assert model.attr.a == 34
    assert model.attr.__class__.__name__ == "RuleA"


def test_abstract_single():
    """
    Test abstract rule with single rule reference.
    """
    grammar = """
    IconSpecification:
        commands*=Command
    ;

    Command:
        ImageCommand
    ;

    ImageCommand:
        'image' '(' image_file=STRING ')'
    ;
    """
    metamodel = metamodel_from_str(grammar)
    metamodel.model_from_str('image("testimage.svg")')

    assert metamodel["IconSpecification"]._tx_type is RULE_COMMON
    assert metamodel["Command"]._tx_type is RULE_ABSTRACT
    assert metamodel["Command"]._tx_inh_by == [metamodel["ImageCommand"]]
    assert metamodel["ImageCommand"]._tx_type is RULE_COMMON


def test_abstract_with_match_rule():
    """To be abstract rule at least one alternative must be either abstract or
    common.
    """

    grammar = """
    Rule: STRING|Rule1|ID;
    Rule1: a='a'; // common rule
    """
    meta = metamodel_from_str(grammar)
    assert meta["Rule"]._tx_type is RULE_ABSTRACT


def test_unreferenced_abstract_rule():
    """
    Test that unreferenced abstract rule is properly recognized.
    """
    grammar = """
    First: name=ID;
    Second: Third;
    Third: a=STRING;
    """
    mm = metamodel_from_str(grammar)

    assert mm["First"]._tx_type == RULE_COMMON
    assert mm["Second"]._tx_type == RULE_ABSTRACT
    assert mm["Second"]._tx_inh_by == [mm["Third"]]
    assert mm["Third"]._tx_type == RULE_COMMON


def test_abstract_rule_with_multiple_match_rule_refs():
    """
    Test that a single alternative of abstract rule can reference multiple
    match rules
    """
    grammar = """
    Rule: STRING|Rule1|ID|Prefix INT Sufix;
    Rule1: a='a'; // common rule
    Prefix: '#';
    Sufix: '--';
    """
    meta = metamodel_from_str(grammar)
    assert meta["Rule"]._tx_type is RULE_ABSTRACT

    model = meta.model_from_str("# 23 --")
    assert model == "#23--"

    model = meta.model_from_str("a")
    assert type(model).__name__ == "Rule1"
    assert model.a == "a"


def test_abstract_rule_with_multiple_rule_refs():
    """
    Test that a single alternative of abstract rule can reference multiple
    match rules with a single common rule.
    """
    grammar = """
    Rule: STRING|Rule1|ID|Prefix Rule1 Sufix;
    Rule1: a=INT; // common rule
    Prefix: '#';
    Sufix: '--';
    """
    meta = metamodel_from_str(grammar)
    model = meta.model_from_str("# 23 --")
    assert meta["Rule"]._tx_type is RULE_ABSTRACT
    assert model.a == 23


def test_abstract_rule_with_multiple_common_rule_refs():
    """
    Test that a single alternative of abstract rule can not reference multiple
    common rules.
    """
    grammar = """
    Rule: STRING|Rule1|ID|Prefix Rule1 Sufix Rule2;  // Reference both Rule1 and Rule2
    Rule1: a=INT; // common rule
    Rule2: a=STRING; // common rule
    Prefix: '#';
    Sufix: '--';
    """  # noqa
    meta = metamodel_from_str(grammar)
    model = meta.model_from_str('# 23 -- "some string"')
    assert meta["Rule"]._tx_type is RULE_ABSTRACT
    # Only Rule1 is returned
    assert model.__class__.__name__ == "Rule1"
    assert model.a == 23


def test_abstract_rule_with_sequence_top_rule():
    """ """
    grammar = """
    Rule: (STRING|Rule1|ID|'#' Rule1) Sufix;
    Rule1: a=INT; // common rule
    Prefix: '#';
    Sufix: '--';
    """
    meta = metamodel_from_str(grammar)
    model = meta.model_from_str("# 23 --")
    assert meta["Rule"]._tx_type is RULE_ABSTRACT
    assert model.a == 23


def test_abstract_rule_with_multiple_references_and_complex_nesting():
    """ """
    grammar = """
    Rule: STRING|ID|'#' Rule1 Sufix;
    Rule1: a=INT; // common rule
    Prefix: '#';
    Sufix: ID | SomeOtherSufix;
    SomeOtherSufix: '--' '#';
    """
    meta = metamodel_from_str(grammar)
    model = meta.model_from_str("# 23 --  #")
    assert meta["Rule"]._tx_type is RULE_ABSTRACT
    assert model.a == 23


def test_match_rule():
    """
    Match rule always returns string.
    """

    grammar = """
    Rule: 'one'|'two'|'three';
    """
    meta = metamodel_from_str(grammar)
    assert meta
    assert meta["Rule"]._tx_type is RULE_MATCH

    model = meta.model_from_str("two")
    assert model
    assert model.__class__ is str
    assert model == "two"


def test_match_rule_multiple():
    """
    If match rule has multiple simple matches resulting string should
    be made by concatenation of simple matches.
    """
    grammar = """
    Rule: 'one' 'two' | 'three';
    """
    meta = metamodel_from_str(grammar)
    assert meta
    assert meta["Rule"]._tx_type is RULE_MATCH

    model = meta.model_from_str(" one two")
    assert model
    assert model.__class__ is str
    assert model == "onetwo"


def test_match_rule_complex():
    """
    Test match rule that has complex expressions.
    """
    grammar = r"""
    Rule: ('one' /\d+/)* 'foo'+ |'two'|'three';
    """
    meta = metamodel_from_str(grammar)
    assert meta
    assert meta["Rule"]._tx_type is RULE_MATCH

    model = meta.model_from_str("one 45 one 78 foo foo foo")
    assert model
    assert model.__class__ is str
    assert model == "one45one78foofoofoo"


def test_match_rule_suppress():
    """
    Test suppressing operator in match rules.
    """
    grammar = r"""
    FullyQualifiedID[noskipws]:
        /\s*/-
        QuotedID+['.']
        /\s*/-
    ;
    QuotedID:
        '"'?- ID '"'?-
    ;
    """

    meta = metamodel_from_str(grammar)
    model = meta.model_from_str(
        """
                                first."second".third."fourth"
                                """
    )
    assert model == "first.second.third.fourth"

    # Checking suppress rule reference
    grammar = """
        First: 'a' Second- Third;
        Second: 'b';
        Third: Second;
    """
    meta = metamodel_from_str(grammar)
    model = meta.model_from_str("a b b")
    # Second b should be suppressed
    assert model == "ab"


def test_rule_single_reference_to_match_rule():
    """
    Test that rule with single reference to match rule is match rule.
    """
    grammar = """
    First: name=ID Second;
    Second: Third;
    Third: STRING|INT;
    """
    mm = metamodel_from_str(grammar)

    assert mm["First"]._tx_type == RULE_COMMON
    assert mm["Second"]._tx_type == RULE_MATCH
    assert mm["Third"]._tx_type == RULE_MATCH


def test_regex_match_rule():
    """
    Match rule always returns string.
    """

    grammar = """
    Rule: 'one'|/bar.?/|'three';
    """
    meta = metamodel_from_str(grammar)
    assert meta
    assert meta["Rule"]._tx_type is RULE_MATCH
    assert set([x.__name__ for x in meta]) == set(["Rule"]).union(set(ALL_TYPE_NAMES))

    model = meta.model_from_str("bar7")
    assert model
    assert model.__class__ is str
    assert model == "bar7"


def test_basetype_match_rule_is_match():
    """
    Test that ordered choice of basetypes is a match rule.
    """
    grammar = """
    Rule: INT|ID;
    """
    meta = metamodel_from_str(grammar)
    assert meta
    assert meta["Rule"]._tx_type is RULE_MATCH

    model = meta.model_from_str("34")
    assert model
    assert model.__class__ is int
    assert model == 34


def test_simple_match_basetype_is_match_rule():
    """
    Test that ordered choice of simple matches and base types
    is a match rule.
    """

    grammar = """
    Rule: INT|'one'|ID;
    """
    meta = metamodel_from_str(grammar)
    assert meta
    assert meta["Rule"]._tx_type is RULE_MATCH

    model = meta.model_from_str("34")
    assert model
    assert model.__class__ is int
    assert model == 34


def test_all_basetypes():
    """
    Test that base types are matched properly.
    """
    grammar = """
        Rule:
            a=FLOAT
            b=INT
            c1=BOOL
            c2=BOOL
            d1=STRING
            d2=STRING
            e=ID
        ;
    """
    meta = metamodel_from_str(grammar)
    assert meta
    assert meta["Rule"]._tx_type is RULE_COMMON
    assert meta["BASETYPE"]._tx_type is RULE_MATCH
    assert meta["NUMBER"]._tx_type is RULE_MATCH
    assert meta["INT"]._tx_type is RULE_MATCH
    assert meta["FLOAT"]._tx_type is RULE_MATCH
    assert meta["STRING"]._tx_type is RULE_MATCH
    assert meta["BOOL"]._tx_type is RULE_MATCH

    model = meta.model_from_str(
        '3.4 5 true 0 "some string" ' "'some other string' some_id"
    )
    assert model.a == 3.4
    assert model.b == 5
    assert model.c1 is True
    assert model.c2 is False
    assert model.d1 == "some string"
    assert model.d2 == "some other string"
    assert model.e == "some_id"


def test_basetype():
    """
    Test that basetype will match each type properly.
    """
    grammar = """
        Rule:
            a1=BASETYPE
            a2=BASETYPE
            a3=BASETYPE
            a4=BASETYPE
            b=BASETYPE
            c=BASETYPE
            d=BASETYPE
            e=BASETYPE
        ;
    """

    meta = metamodel_from_str(grammar)
    assert meta
    assert meta["Rule"]._tx_type is RULE_COMMON

    model = meta.model_from_str('False false true True 0 4.5 "string" some_id')

    assert model.a1 is False
    assert model.a2 is False
    assert model.a3 is True
    assert model.a4 is True
    assert model.b == 0
    assert model.c == 4.5
    assert model.d == "string"
    assert model.e == "some_id"


def test_float_int_number():
    """
    Test that numbers are recognized correctly.
    """
    grammar = """
        Rule:
            a=NUMBER
            b=INT
            c=FLOAT
        ;
    """
    meta = metamodel_from_str(grammar)

    model = meta.model_from_str("3.4 5 .3")
    assert model.a == 3.4
    assert isinstance(model.a, float)
    assert model.b == 5
    assert model.c == 0.3

    model = meta.model_from_str("3 5 2.0")
    assert model.a == 3
    assert isinstance(model.a, int)

    assert model.b == 5
    assert model.c == 2
    assert isinstance(model.c, float)


def test_float_variations():
    """
    Test different float formats and boundary anchoring.
    """
    grammar = """
        Rule: a*=FLOAT[','] ',' some_id='7i'
        ;
    """
    meta = metamodel_from_str(grammar)

    model = meta.model_from_str("3.5, .4, 5.0, 6., 7i")
    assert len(model.a) == 4
    assert isinstance(model.a[0], float)
    assert isinstance(model.a[1], float)
    assert isinstance(model.a[2], float)
    assert isinstance(model.a[3], float)
    assert model.some_id == "7i"

    # Check scientific notation
    model = meta.model_from_str("1e-2, 7i")
    assert model.a[0] == 0.01


def test_string_escaping():
    """
    Test quotes escaping inside strings.
    """
    grammar = """
        Rule: a+=STRING[','];
    """
    meta = metamodel_from_str(grammar)

    model = meta.model_from_str(
        r"""
    "Double quotes string", "Double quotes with 'single quotes embedded'",
    "Double quotes with \" escaped quotes",
    'Single quotes string', 'Single quotes with "double quotes embedded"',
    'Single quotes with \' escaped single quotes'
    """
    )

    assert model.a[0] == r"Double quotes string"
    assert model.a[1] == r"Double quotes with 'single quotes embedded'"
    assert model.a[2] == r'Double quotes with " escaped quotes'
    assert model.a[3] == r"Single quotes string"
    assert model.a[4] == r'Single quotes with "double quotes embedded"'
    assert model.a[5] == r"Single quotes with ' escaped single quotes"


def test_rule_call_forward_backward_reference():
    grammar = """
    Model: 'start' attr=Rule2;
    Rule1: 'one'|'two'|'three';
    Rule2: 'rule2' attr=Rule1;
    """
    meta = metamodel_from_str(grammar)
    assert meta
    assert set([x.__name__ for x in meta]) == set(["Model", "Rule1", "Rule2"]).union(
        set(ALL_TYPE_NAMES)
    )

    model = meta.model_from_str("start rule2 three")
    assert model
    assert model.attr
    assert model.attr.attr
    assert model.attr.attr == "three"


def test_assignment_zeroormore():
    grammar = """
    Model: 'start' attr*=Rule;     // There should be zero or more Rule-s after
                                    // 'start'
    Rule: Rule1|Rule2|Rule3;
    Rule1: a=INT;
    Rule2: b=STRING;
    Rule3: c=ID;
    """
    meta = metamodel_from_str(grammar)
    assert meta
    assert set([x.__name__ for x in meta]) == set(
        ["Model", "Rule", "Rule1", "Rule2", "Rule3"]
    ).union(set(ALL_TYPE_NAMES))

    model = meta.model_from_str('start 34 "foo"')
    assert model
    assert model.attr
    assert model.attr[0].a == 34
    assert model.attr[1].b == "foo"
    assert model.attr[0].__class__.__name__ == "Rule1"
    assert model.attr[1].__class__.__name__ == "Rule2"

    model = meta.model_from_str("start")
    assert model


def test_assignment_multiple_simple():
    """
    Test that multiple assignments to the same attribute will result in the
    list of values.
    """

    grammar = """
    Model: 'start' a=INT a=INT (a=INT)?;
    """
    meta = metamodel_from_str(grammar)

    model = meta.model_from_str("start 34 23 45")

    assert meta["Model"]._tx_attrs["a"].cls.__name__ == "INT"
    assert meta["Model"]._tx_attrs["a"].mult == "1..*"
    assert meta["Model"]._tx_attrs["a"].cont
    assert not meta["Model"]._tx_attrs["a"].ref
    assert model
    assert model.a
    assert isinstance(model.a, list)
    assert len(model.a) == 3
    assert model.a == [34, 23, 45]

    model = meta.model_from_str("start 34 23")
    assert model.a == [34, 23]


def test_assignment_multiple_different():
    """
    Test that multiple assignments of different type will result in a list of
    OBJECT.
    """

    grammar = """
    Model:
        elements*=Element
    ;
    Element:
       name=ID value=STRING | name=ID value=INT value=ID
    ;

    """
    mm = metamodel_from_str(grammar)
    assert mm["Element"]._tx_attrs["name"].cls.__name__ == "ID"
    assert mm["Element"]._tx_attrs["name"].mult == "1"
    assert not mm["Element"]._tx_attrs["name"].ref
    assert mm["Element"]._tx_attrs["value"].cls.__name__ == "OBJECT"
    assert mm["Element"]._tx_attrs["value"].mult == "1..*"
    assert mm["Element"]._tx_attrs["value"].ref


def test_assignment_oneoormore():
    grammar = """
    Model: 'start' attr+=Rule;    // There should be at least one Rule
                                 // after 'start'
    Rule: Rule1|Rule2|Rule3;
    Rule1: a=INT;
    Rule2: b=STRING;
    Rule3: c=ID;
    """
    meta = metamodel_from_str(grammar)
    assert meta
    assert set([x.__name__ for x in meta]) == set(
        ["Model", "Rule", "Rule1", "Rule2", "Rule3"]
    ).union(set(ALL_TYPE_NAMES))

    model = meta.model_from_str('start 34 "foo"')
    assert model
    assert model.attr
    assert model.attr[0].a == 34
    assert model.attr[1].b == "foo"
    assert model.attr[0].__class__.__name__ == "Rule1"
    assert model.attr[1].__class__.__name__ == "Rule2"

    # There must be at least one Rule matched after 'start'
    with pytest.raises(TextXSyntaxError):
        model = meta.model_from_str("start")
    assert model


def test_assignment_optional():
    grammar = """
    Model: 'start' (attr=Rule)?;    // There should be at most one Rule
                                 // after 'start'
    Rule: Rule1|Rule2|Rule3;
    Rule1: a=INT;
    Rule2: b=STRING;
    Rule3: c=ID;
    """
    meta = metamodel_from_str(grammar)
    assert meta
    assert set([x.__name__ for x in meta]) == set(
        ["Model", "Rule", "Rule1", "Rule2", "Rule3"]
    ).union(set(ALL_TYPE_NAMES))

    model = meta.model_from_str("start")
    assert model
    model = meta.model_from_str("start 34")
    assert model
    assert model.attr
    assert model.attr.a == 34
    assert model.attr.__class__.__name__ == "Rule1"

    # There must be at most one Rule matched after 'start'
    with pytest.raises(TextXSyntaxError):
        model = meta.model_from_str('start 34 "foo"')
    assert model


def test_repetition_separator_modifier():
    """
    Match list with regex separator.
    """

    grammar = """
    Model: 'start' attr+=Rule[/,|;/];   // Here a regex match is used to
                                        // define , or ; as a separator
    Rule: Rule1|Rule2|Rule3;
    Rule1: a=INT;
    Rule2: b=STRING;
    Rule3: c=ID;
    """
    meta = metamodel_from_str(grammar)
    assert meta
    assert set([x.__name__ for x in meta]) == set(
        ["Model", "Rule", "Rule1", "Rule2", "Rule3"]
    ).union(set(ALL_TYPE_NAMES))

    model = meta.model_from_str('start 34, "foo"; ident')
    assert model
    assert model.attr
    assert model.attr[0].a == 34
    assert model.attr[1].b == "foo"
    assert model.attr[2].c == "ident"
    assert model.attr[0].__class__.__name__ == "Rule1"
    assert model.attr[1].__class__.__name__ == "Rule2"
    assert model.attr[2].__class__.__name__ == "Rule3"

    # There must be at least one Rule matched after 'start'
    with pytest.raises(TextXSyntaxError):
        model = meta.model_from_str("start")
    assert model


def test_bool_match():
    grammar = """
    Model: 'start' rule?='rule' rule2?=Rule;   // rule and rule2 attr should be
    Rule: Rule1|Rule2|Rule3;                    // true where match succeeds
    Rule1: a=INT;
    Rule2: b=STRING;
    Rule3: c=ID;
    """
    meta = metamodel_from_str(grammar)
    assert meta
    assert set([x.__name__ for x in meta]) == set(
        ["Model", "Rule", "Rule1", "Rule2", "Rule3"]
    ).union(set(ALL_TYPE_NAMES))

    model = meta.model_from_str("start rule 34")
    assert model
    assert hasattr(model, "rule")
    assert hasattr(model, "rule2")
    assert model.rule is True
    assert model.rule2 is True

    model = meta.model_from_str("start 34")
    assert model.rule is False
    assert model.rule2 is True

    model = meta.model_from_str("start")
    assert model.rule is False
    assert model.rule2 is False


def test_object_and_rule_reference():
    grammar = """
    Model: 'start' rules*=RuleA 'ref' ref=[RuleA];
    RuleA: 'rule' name=ID;
    """
    meta = metamodel_from_str(grammar)
    assert meta
    assert set([x.__name__ for x in meta]) == set(["Model", "RuleA"]).union(
        set(ALL_TYPE_NAMES)
    )

    model = meta.model_from_str("start rule rule1 rule rule2 ref rule1")
    assert model
    assert hasattr(model, "rules")
    assert hasattr(model, "ref")
    assert model.rules
    assert model.ref

    # Reference to first rule
    assert model.ref is model.rules[0]
    assert model.ref.__class__.__name__ == "RuleA"


def test_abstract_rule_and_object_reference():
    grammar = """
    Model: 'start' rules*=RuleA 'ref' ref=[RuleA];
    RuleA: Rule1|Rule2;
    Rule1: RuleI|RuleE;
    Rule2: 'r2' name=ID;
    RuleI: 'rI' name=ID;
    RuleE: 'rE' name=ID;
    """
    meta = metamodel_from_str(grammar)
    assert meta
    assert set([x.__name__ for x in meta]) == set(
        ["Model", "RuleA", "Rule1", "Rule2", "RuleI", "RuleE"]
    ).union(set(ALL_TYPE_NAMES))

    model = meta.model_from_str("start r2 rule1 rE rule2 ref rule2")
    assert model
    assert hasattr(model, "rules")
    assert hasattr(model, "ref")
    assert model.rules
    assert model.ref

    # Reference to first rule
    assert model.ref is model.rules[1]
    assert model.ref.__class__.__name__ == "RuleE"


def test_repeat_rule_ref():
    grammar = """
    Rule: ID*;
    """
    metamodel = metamodel_from_str(grammar)

    assert metamodel["Rule"]._tx_type is RULE_MATCH
    model = metamodel.model_from_str("""first second third""")
    assert model == "firstsecondthird"


def test_repeat_strmatch():
    grammar = """
    Rule: "first"*;
    """
    metamodel = metamodel_from_str(grammar)

    model = metamodel.model_from_str("""first first""")
    assert metamodel["Rule"]._tx_type is RULE_MATCH
    assert model == "firstfirst"


def test_repeat_strmatch_with_separator():
    grammar = """
    Rule: "first"*[','];
    """
    metamodel = metamodel_from_str(grammar)

    assert metamodel["Rule"]._tx_type is RULE_MATCH
    model = metamodel.model_from_str("""first, first""")
    assert model == "first,first"


def test_empty_strmatch():
    """
    Test empty str match.
    """
    grammar = """
    Rule: first='' 'a';
    """
    mm = metamodel_from_str(grammar)
    model = mm.model_from_str("a")
    assert model


def test_empty_regexmatch():
    """
    Test empty regex match.
    Note, there must be some regex-code between slashes or else it will be
    parsed as line comment, e.g. "()".
    """
    grammar = """
    Rule: first=/()/ 'a';
    """
    mm = metamodel_from_str(grammar)
    model = mm.model_from_str("a")
    assert model

    grammar = """
    Rule: first=// 'a';
    """
    with pytest.raises(TextXSyntaxError):
        metamodel_from_str(grammar)


def test_default_attribute_values():
    """
    Test default values for unsupplied base type
    attributes.
    """
    grammar = """
    First:
        'first' seconds+=Second
        ('A' a=INT)?
        ('B' b=BOOL)?
        ('C' c=STRING)?
        ('D' d=FLOAT)?
        ('E' e+=INT)?
        ('F' f*=INT)?
        ('G' g?=INT)?
    ;

    Second:
        INT|STRING
    ;
    """
    metamodel = metamodel_from_str(grammar)

    model = metamodel.model_from_str(
        """
            first 45 "foo" 78
    """
    )
    assert type(model).__name__ == "First"
    assert isinstance(model.seconds, list)
    assert isinstance(model.a, int)
    assert model.a == 0
    assert isinstance(model.b, bool)
    assert model.b is False
    assert isinstance(model.c, str)
    assert model.c == ""
    assert isinstance(model.d, float)
    assert model.d == 0.0
    assert isinstance(model.e, list)
    assert model.e == []
    assert isinstance(model.f, list)
    assert model.f == []
    assert isinstance(model.g, bool)
    assert model.g is False


def test_sequence_ordered_choice():
    """
    Test ordered choice of sequences.
    """

    grammar = """
    Model:
        ('first' a=INT b?='a_is_here' |
        'second' c=INT d?='c_is_here' |
        e=RuleA)
        'END'
    ;
    RuleA: 'rule' name=ID;
    """
    meta = metamodel_from_str(grammar, debug=True)
    assert meta
    assert set([x.__name__ for x in meta]) == set(["Model", "RuleA"]).union(
        set(ALL_TYPE_NAMES)
    )

    model = meta.model_from_str("first 23 a_is_here END")
    assert model.a == 23
    assert model.c == 0
    assert model.b is True
    assert model.d is False
    model = meta.model_from_str("second 32 END")
    assert model.a == 0
    assert model.c == 32
    assert model.b is False
    assert model.d is False
    model = meta.model_from_str("rule A END")
    assert model.a == 0
    assert model.c == 0
    assert model.b is False
    assert model.d is False


def test_syntactic_predicate_not():
    """
    Test negative lookahead using `not` syntactic predicate.
    """
    grammar = """
    Expression: Let | MyID | NUMBER;
    Let:
        'let'
            expr+=Expression
        'end'
    ;

    Keyword: 'let' | 'end';
    MyID: !Keyword ID;
    """
    meta = metamodel_from_str(grammar)

    model = meta.model_from_str(
        """
                                let let let 34 end let foo end end end
                                """
    )

    assert model
    assert len(model.expr) == 1
    assert model.expr[0].expr[0].expr[0] == 34
    assert model.expr[0].expr[1].expr[0] == "foo"


def test_syntactic_predicate_and():
    """
    Test positive lookahead using `and` syntactic predicate.
    """
    grammar = """
    Model: elements+=Element;
    Element: AbeforeB | A | B;
    AbeforeB:  a='a' &'b';      // this succeeds only if 'b' follows 'a'
    A: a='a';
    B: a='b';
    """
    meta = metamodel_from_str(grammar)

    model = meta.model_from_str("a a a b")

    assert model
    assert len(model.elements) == 4
    assert model.elements[0].__class__.__name__ == "A"
    assert model.elements[1].__class__.__name__ == "A"
    assert model.elements[2].__class__.__name__ == "AbeforeB"
    assert model.elements[3].__class__.__name__ == "B"
