import pytest  # noqa
from textx import metamodel_from_str


def test_unicode_grammar_from_string():
    """
    Test grammar with unicode char given in grammar string.
    """

    grammar = """
    First:
        'first' a = Second
    ;

    Second:
        "Ω"|"±"|"♪"
    ;

    """

    model_str = """
    first ♪
    """

    metamodel = metamodel_from_str(grammar)
    assert metamodel
    model = metamodel.model_from_str(model_str)
    assert model.a == "♪"
