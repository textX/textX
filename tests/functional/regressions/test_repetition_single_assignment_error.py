import pytest  # noqa
from textx.metamodel import metamodel_from_str
from textx.exceptions import TextXSemanticError


def test_repetition_single_assignment_error():
    """
    Test that plain assignment in repetition end up being a list in the model.
    """

    grammar = r"""
    Rep: many_a*=A;
    A: 'A'
      ( ('b' '=' b=BOOL) |
        ('c' '=' c=C)
      )*;
    B: "b";
    C: "c";
    """
    mm = metamodel_from_str(grammar)
    model = mm.model_from_str(" A c=c b=true ")

    assert model.many_a[0].b == [True]
    assert model.many_a[0].c == ["c"]

    grammar = r"""
    Rep: a=A;
    A: (('b' '=' b=BOOL) |
       ('c' '=' c=C))*;
    B: "b";
    C: "c";
    """
    mm = metamodel_from_str(grammar)
    model = mm.model_from_str(" c=c b=true c=c b=false")

    assert model.a.b == [True, False]
    assert model.a.c == ["c", "c"]


def test_repetition_bool_assignment_error():
    """
    Test error with repetition of boolean assignment.
    """

    grammar = r"""
    TestInstance: (practice?="practice"|randomize?="randomize")*;
    """
    with pytest.raises(TextXSemanticError):
        mm = metamodel_from_str(grammar)

    grammar = r"""
    TestInstance: (practice?="practice"|randomize?="randomize")#;
    """
    mm = metamodel_from_str(grammar)
    model = mm.model_from_str(" randomize ")

    assert model.randomize
    assert not model.practice
