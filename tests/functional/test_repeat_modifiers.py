from __future__ import unicode_literals
import pytest
from textx.metamodel import metamodel_from_str
from textx.exceptions import TextXSyntaxError


def test_modifier_separator_zeroormore():
    model = """
    Rule:
        ("a"|"b")*[','];
    """
    metamodel = metamodel_from_str(model)

    model = metamodel.model_from_str("a,b, a, b")
    assert model


def test_modifier_separator_oneormore():
    model = """
    Rule:
        ("a"|"b")+[','];
    """
    metamodel = metamodel_from_str(model)

    model = metamodel.model_from_str("a,b, a, b")
    assert model

    with pytest.raises(TextXSyntaxError):
        # Must be separated with comma
        metamodel.model_from_str("a b")

    with pytest.raises(TextXSyntaxError):
        # At least one must be matched
        metamodel.model_from_str("")


def test_modifier_separator_optional():
    model = """
    Rule:
        ("a"|"b")?[','];
    """
    with pytest.raises(TextXSyntaxError):
        # Modifiers are not possible for ? operator
        metamodel_from_str(model)


def test_assignment_modifier_separator_zeroormore():
    model = """
    Rule:
        a*=AorB[','];
    AorB:
        "a"|"b";
    """
    metamodel = metamodel_from_str(model)

    model = metamodel.model_from_str("a,b, a")
    # 3 AorBs must be matched
    assert len(model.a) == 3
    assert model.a[1] == 'b'


def test_assignment_modifier_separator_oneormore():
    model = """
    Rule:
        a+=AorB[','];
    AorB:
        "a"|"b";
    """
    metamodel = metamodel_from_str(model)

    model = metamodel.model_from_str("a,b, a")
    # 3 AorBs must be matched
    assert len(model.a) == 3
    assert model.a[1] == 'b'


def test_assignment_modifier_separator_optional():
    model = """
    Rule:
        a?=AorB[','];
    AorB:
        "a"|"b";
    """
    with pytest.raises(TextXSyntaxError):
        metamodel_from_str(model)


def test_modifier_eolterm_zeroormore():
    model = """
    Rule:
        ID+[eolterm] 'nextline';
    """
    metamodel = metamodel_from_str(model)

    model = metamodel.model_from_str("""first second third
    nextline
    """)
    assert model


