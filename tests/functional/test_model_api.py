"""
Model query and navigation API.
"""
import pytest
from textx.metamodel import metamodel_from_str
from textx.model import children_of_type, parent_of_type, model_root


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


def test_children_of_type():

    metamodel = metamodel_from_str(grammar)
    model = metamodel.model_from_str(model_str)

    thirds = children_of_type(model, 'Third')
    assert len(thirds) == 5
    assert set(['first', 'second', 'third', 'one', 'two']) \
        == set([a.x for a in thirds])

    # Test search in the part of the model
    thirds = children_of_type(model.a[1], "Third")
    assert len(thirds) == 1
    assert 'two' == list(thirds)[0].x


def test_parent_of_type():

    metamodel = metamodel_from_str(grammar)
    model = metamodel.model_from_str(model_str)

    t = model.a[0].y
    s = parent_of_type(t, 'Second')
    assert s.__class__.__name__ == 'Second'
    assert s.x[0] == 23
    f = parent_of_type(t, 'First')
    assert f.__class__.__name__ == 'First'
    assert f is model


def test_model_root():

    metamodel = metamodel_from_str(grammar)
    model = metamodel.model_from_str(model_str)

    t = model.a[0].y
    assert model_root(t) is model
