import pytest

from textx.metamodel import metamodel_from_str
from textx.textx import BASE_TYPE_NAMES
from textx.exceptions import TextXSyntaxError


def test_normal_rule():

    rule = """
    Model: a = 'something';
    """
    meta = metamodel_from_str(rule)
    assert meta

    model = meta.model_from_str('something')
    assert model
    assert model.__class__.__name__ == "Model"
    assert model.a == "something"


def test_match_rule():
    """
    Match rule always returns string.
    """

    rule = """
    Rule: 'one'|'two'|'three';
    """
    meta = metamodel_from_str(rule)
    assert meta

    model = meta.model_from_str('two')
    assert model
    assert model.__class__ == str
    assert model == "two"


def test_regex_match_rule():
    """
    Match rule always returns string.
    """

    rule = """
    Rule: 'one'|/bar.?/|'three';
    """
    meta = metamodel_from_str(rule)
    assert meta
    assert set(meta.keys()) == set(['Rule'])\
        .union(set(BASE_TYPE_NAMES))

    model = meta.model_from_str('bar7')
    assert model
    assert model.__class__ == str
    assert model == "bar7"


def test_rule_call_forward_backward_reference():

    rule = """
    Model: 'start' attr=Rule2;
    Rule1: 'one'|'two'|'three';
    Rule2: 'rule2' attr=Rule1;
    """
    meta = metamodel_from_str(rule)
    assert meta
    assert set(meta.keys()) == set(['Model', 'Rule1', 'Rule2'])\
        .union(set(BASE_TYPE_NAMES))

    model = meta.model_from_str('start rule2 three')
    assert model
    assert model.attr
    assert model.attr.attr
    assert model.attr.attr == "three"


def test_abstract_rule():

    rule = """
    Model: 'start' attr=Rule;
    Rule: Rule1|Rule2|Rule3;
    Rule1: RuleA|RuleB;
    RuleA: a=INT;
    RuleB: a=STRING;
    Rule2: b=STRING;
    Rule3: c=ID;
    """
    meta = metamodel_from_str(rule)
    assert meta
    assert set(meta.keys()) == set(['Model', 'Rule', 'RuleA', 'RuleB', 'Rule1', 'Rule2', 'Rule3'])\
        .union(set(BASE_TYPE_NAMES))

    model = meta.model_from_str('start 34')
    assert model
    assert model.attr
    assert model.attr.a == 34
    assert model.attr.__class__.__name__ == 'RuleA'


def test_list_zeroormore():

    rule = """
    Model: 'start' attr*=Rule;     // There should be zero or more Rule-s after
                                    // 'start'
    Rule: Rule1|Rule2|Rule3;
    Rule1: a=INT;
    Rule2: b=STRING;
    Rule3: c=ID;
    """
    meta = metamodel_from_str(rule)
    assert meta
    assert set(meta.keys()) == set(['Model', 'Rule', 'Rule1', 'Rule2', 'Rule3'])\
        .union(set(BASE_TYPE_NAMES))

    model = meta.model_from_str('start 34 "foo"')
    assert model
    assert model.attr
    assert model.attr[0].a == 34
    assert model.attr[1].b == "foo"
    assert model.attr[0].__class__.__name__ == 'Rule1'
    assert model.attr[1].__class__.__name__ == 'Rule2'

    model = meta.model_from_str('start')
    assert model


def test_list_oneoormore():

    rule = """
    Model: 'start' attr+=Rule;    // There should be at least one Rule
                                 // after 'start'
    Rule: Rule1|Rule2|Rule3;
    Rule1: a=INT;
    Rule2: b=STRING;
    Rule3: c=ID;
    """
    meta = metamodel_from_str(rule)
    assert meta
    assert set(meta.keys()) == set(['Model', 'Rule', 'Rule1', 'Rule2', 'Rule3'])\
        .union(set(BASE_TYPE_NAMES))

    model = meta.model_from_str('start 34 "foo"')
    assert model
    assert model.attr
    assert model.attr[0].a == 34
    assert model.attr[1].b == "foo"
    assert model.attr[0].__class__.__name__ == 'Rule1'
    assert model.attr[1].__class__.__name__ == 'Rule2'

    # There must be at least one Rule matched after 'start'
    with pytest.raises(TextXSyntaxError):
        model = meta.model_from_str('start')
    assert model


def test_list_separator():
    """
    Match list with regex separator.
    """

    rule = """
    Model: 'start' attr+=Rule[/,|;/];   // Here a regex match is used to
                                        // define , or ; as a separator
    Rule: Rule1|Rule2|Rule3;
    Rule1: a=INT;
    Rule2: b=STRING;
    Rule3: c=ID;
    """
    meta = metamodel_from_str(rule)
    assert meta
    assert set(meta.keys()) == set(['Model', 'Rule', 'Rule1', 'Rule2', 'Rule3'])\
        .union(set(BASE_TYPE_NAMES))

    model = meta.model_from_str('start 34, "foo"; ident')
    assert model
    assert model.attr
    assert model.attr[0].a == 34
    assert model.attr[1].b == "foo"
    assert model.attr[2].c == "ident"
    assert model.attr[0].__class__.__name__ == 'Rule1'
    assert model.attr[1].__class__.__name__ == 'Rule2'
    assert model.attr[2].__class__.__name__ == 'Rule3'

    # There must be at least one Rule matched after 'start'
    with pytest.raises(TextXSyntaxError):
        model = meta.model_from_str('start')
    assert model


def test_bool_match():
    rule = """
    Model: 'start' rule?='rule' rule2?=Rule;   // rule and rule2 attr should be
    Rule: Rule1|Rule2|Rule3;                    // true where match succeeds
    Rule1: a=INT;
    Rule2: b=STRING;
    Rule3: c=ID;
    """
    meta = metamodel_from_str(rule)
    assert meta
    assert set(meta.keys()) == set(['Model', 'Rule', 'Rule1', 'Rule2', 'Rule3'])\
        .union(set(BASE_TYPE_NAMES))

    model = meta.model_from_str('start rule 34')
    assert model
    assert hasattr(model, 'rule')
    assert hasattr(model, 'rule2')
    assert model.rule is True
    assert model.rule2 is True

    model = meta.model_from_str('start 34')
    assert model.rule is False
    assert model.rule2 is True

    model = meta.model_from_str('start')
    assert model.rule is False
    assert model.rule2 is False


def test_rule_reference():
    rule = """
    Model: 'start' rules*=RuleA 'ref' ref=[RuleA];
    RuleA: 'rule' name=ID;
    """
    meta = metamodel_from_str(rule)
    assert meta
    assert set(meta.keys()) == set(['Model', 'RuleA'])\
        .union(set(BASE_TYPE_NAMES))

    model = meta.model_from_str('start rule rule1 rule rule2 ref rule1')
    assert model
    assert hasattr(model, 'rules')
    assert hasattr(model, 'ref')
    assert model.rules
    assert model.ref

    # Reference to first rule
    assert model.ref is model.rules[0]
    assert model.ref.__class__.__name__ == "RuleA"


def test_abstract_rule_reference():
    rule = """
    Model: 'start' rules*=RuleA 'ref' ref=[RuleA];
    RuleA: Rule1|Rule2;
    Rule1: RuleI|RuleE;
    Rule2: 'r2' name=ID;
    RuleI: 'rI' name=ID;
    RuleE: 'rE' name=ID;
    """
    meta = metamodel_from_str(rule)
    assert meta
    assert set(meta.keys()) == set(['Model', 'RuleA', 'Rule1', 'Rule2', 'RuleI', 'RuleE'])\
        .union(set(BASE_TYPE_NAMES))

    model = meta.model_from_str('start r2 rule1 rE rule2 ref rule2')
    assert model
    assert hasattr(model, 'rules')
    assert hasattr(model, 'ref')
    assert model.rules
    assert model.ref

    # Reference to first rule
    assert model.ref is model.rules[1]
    assert model.ref.__class__.__name__ == "RuleE"
# def test_repetition_zeroormore()
