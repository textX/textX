import pytest

from textx import TextXSyntaxError, metamodel_from_str


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


def test_modifier_separator_unordered_group():
    model = """
    Rule:
        ("a" "b" "c")#[','];
    """
    metamodel = metamodel_from_str(model)

    model = metamodel.model_from_str("a, b, c")
    assert model
    model = metamodel.model_from_str("c, a, b")
    assert model

    with pytest.raises(TextXSyntaxError):
        metamodel.model_from_str("a, c b")

    with pytest.raises(TextXSyntaxError):
        metamodel.model_from_str("a, c, a, b")

    with pytest.raises(TextXSyntaxError):
        metamodel.model_from_str(",a, c, b")

    with pytest.raises(TextXSyntaxError):
        metamodel.model_from_str("a, c, b, ")

    with pytest.raises(TextXSyntaxError):
        metamodel.model_from_str("a, c, ,b ")


def test_modifier_separator_unordered_group_with_optionals():
    model = """
    Rule:
        ("a" "b"? "c")#[','];
    """
    metamodel = metamodel_from_str(model)

    model = metamodel.model_from_str("a, b, c")
    assert model
    model = metamodel.model_from_str("c, a")
    assert model

    with pytest.raises(TextXSyntaxError):
        metamodel.model_from_str("a, c b")

    with pytest.raises(TextXSyntaxError):
        metamodel.model_from_str("a, c, ")

    with pytest.raises(TextXSyntaxError):
        metamodel.model_from_str("a, c, a, b")

    with pytest.raises(TextXSyntaxError):
        metamodel.model_from_str(",a, c, b")

    with pytest.raises(TextXSyntaxError):
        metamodel.model_from_str("a, c, b, ")

    with pytest.raises(TextXSyntaxError):
        metamodel.model_from_str("a, c, ,b ")


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
    assert model.a[1] == "b"


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
    assert model.a[1] == "b"


def test_assignment_modifier_separator_optional():
    """
    Modifiers are not allowed for ?= assignment.
    """
    model = """
    Rule:
        a?=AorB[','];
    AorB:
        "a"|"b";
    """
    with pytest.raises(TextXSyntaxError):
        metamodel_from_str(model)


def test_assignment_modifier_separator_plain():
    """
    Modifiers are not allowed for plain assignment.
    """
    model = """
    Rule:
        a=AorB[','];
    AorB:
        "a"|"b";
    """
    with pytest.raises(TextXSyntaxError):
        metamodel_from_str(model)


def test_modifier_eolterm_zeroormore():
    model = """
    Rule:
        'first'
        INT*[eolterm] '123456';
    """
    metamodel = metamodel_from_str(model)

    # After 'first' and before newline must
    # be one or more integers
    with pytest.raises(TextXSyntaxError):
        model = metamodel.model_from_str(
            """
            first
            34 56 88 65
            123456
        """
        )

    # When newline is found matching integers
    # finishes and than a '123456' is matched
    model = metamodel.model_from_str(
        """
        first 34 56 88 65
        123456
    """
    )
    assert model


def test_modifier_eolterm_oneormore():
    model = """
    Rule:
        'first'
        INT+[eolterm] '123456';
    """
    metamodel = metamodel_from_str(model)

    # After 'first' and before newline must
    # be one or more integers
    with pytest.raises(TextXSyntaxError):
        model = metamodel.model_from_str(
            """
            first
            34 56 88 65
            123456
        """
        )

    # When newline is found matching integers
    # finishes and than a '123456' is matched
    model = metamodel.model_from_str(
        """
        first 34 56 88 65
        123456
    """
    )
    assert model


def test_multiple_modifiers():
    """
    Multiple modifier may be specified separated with space.
    """
    model = """
    Rule:
        'first'
        INT+[eolterm ','] '123456';
    """
    metamodel = metamodel_from_str(model)

    # After 'first' and before newline must
    # be one or more integers separated with comma
    with pytest.raises(TextXSyntaxError):
        model = metamodel.model_from_str(
            """
            first
            34 56 88 65
            123456
        """
        )

    # When newline is found matching integers
    # finishes and than a '123456' is matched
    model = metamodel.model_from_str(
        """
        first 34, 56, 88, 65
        123456
    """
    )
    assert model
