"""
Tests for issue: https://github.com/textX/textX/issues/358
Usage of ordered choice in unordered groups.
"""
import pytest

from textx import TextXSyntaxError, metamodel_from_str


@pytest.mark.parametrize(
    "grammar",
    [
        r"""
    Unordered: 'begin' (first?='first' second?='second')#;
    """,
        r"""
    Unordered: 'begin' (first?='first' | second?='second')#;
    """,
    ],
)
def test_unordered_group_sequence_choice(grammar):
    """
    Test the equivalence of using sequence and ordered choice in optional matches in
    unordered groups.
    """
    mm = metamodel_from_str(grammar)

    model = mm.model_from_str("begin second")
    assert model.second and not model.first
    model = mm.model_from_str("begin first")
    assert model.first and not model.second
    model = mm.model_from_str("begin first second")
    assert model.first and model.second
    model = mm.model_from_str("begin second first")
    assert model.first and model.second
    model = mm.model_from_str("begin")
    assert not model.first and not model.second

    with pytest.raises(TextXSyntaxError):
        mm.model_from_str("begin first second first")

    with pytest.raises(TextXSyntaxError):
        mm.model_from_str("begin first first")


@pytest.mark.parametrize(
    "grammar",
    [
        r"""
    Unordered: 'begin' (first='first' second='second')#;
    """,
        r"""
    Unordered: 'begin' (first='first' | second='second')#;
    """,
    ],
)
def test_unordered_group_sequence_choice_nonoptional(grammar):
    """
    Test the equivalence of using sequence and ordered choice in unordered groups.
    """
    mm = metamodel_from_str(grammar)

    model = mm.model_from_str("begin first second")
    assert model.first == "first" and model.second == "second"
    model = mm.model_from_str("begin second first")
    assert model.first == "first" and model.second == "second"

    with pytest.raises(TextXSyntaxError):
        mm.model_from_str("begin first second first")

    with pytest.raises(TextXSyntaxError):
        mm.model_from_str("begin first first")


@pytest.mark.parametrize(
    "grammar",
    [
        r"""
    Unordered: 'begin' (first='first' second='second' | third='third')#;
    """,
        r"""
    Unordered: 'begin' ((first='first' second='second')  third='third')#;
    """,
    ],
)
def test_unordered_group_choice_with_sequences(grammar):
    """
    Test the equivalence of using ordered choice and a sequence of parenthesed groups.
    """
    mm = metamodel_from_str(grammar)

    model = mm.model_from_str("begin first second third")
    assert model.first == "first" and model.second == "second" and model.third == "third"
    model = mm.model_from_str("begin third first second")
    assert model.first == "first" and model.second == "second" and model.third == "third"

    with pytest.raises(TextXSyntaxError):
        mm.model_from_str("begin second first third")

    with pytest.raises(TextXSyntaxError):
        mm.model_from_str("begin third second first")


def test_unordered_group_with_optional_assignments():
    """
    Test for a question raised during the code review:
    https://github.com/textX/textX/pull/359
    """
    grammar = r"""
    Root: 'begin' a=Unordered;
    Unordered: (first?='first' second?='second' | third?='third')#;
    """

    mm = metamodel_from_str(grammar)
    m = mm.model_from_str("begin")
    # TODO: Maybe we shall have m.a not None and all its attributes to be None.
    assert m.a is None
