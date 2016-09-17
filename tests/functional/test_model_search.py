"""
Tests model search and navigation.
"""
import pytest
from textx.metamodel import metamodel_from_str
from textx.model import all_of_type


def test_all_of_type():

    grammar = """
    First:
        a+=Second
        b*=Third
    ;

    Second:
        x+=INT[','] (':' y=Third)?
    ;

    Third:
        x=STRING
    ;
    """

    model_str = """
        23, 45, 56 : "one"
        53, 56, 87 : "two"
        23, 45, 77
        "first" "second" "third"
    """

    metamodel = metamodel_from_str(grammar)
    model = metamodel.model_from_str(model_str)

    thirds = all_of_type(metamodel, model, 'Third' )
    assert len(thirds) == 5
    assert set(['first', 'second', 'third', 'one', 'two']) \
        == set([a.x for a in thirds])

    # Test search in the part of the model
    thirds = all_of_type(metamodel, model.a[1], "Third")
    assert len(thirds) == 1
    assert 'two' == list(thirds)[0].x


