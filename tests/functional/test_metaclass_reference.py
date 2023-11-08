import os

import pytest

from textx import metamodel_from_file, metamodel_from_str

grammar = """
First:
    'first' seconds+=Second
;

Second:
    value=INT|value=STRING
;

"""


def test_metaclass_ref():
    metamodel = metamodel_from_str(grammar)
    First = metamodel["First"]
    Second = metamodel["Second"]

    model = metamodel.model_from_str('first 45 "test" 12')

    assert type(model) is First
    assert all(type(x) is Second for x in model.seconds)


def test_metaclass_user_class():
    """
    User supplied meta class.
    """

    class First:
        def __init__(self, seconds):
            self.seconds = seconds

    metamodel = metamodel_from_str(grammar, classes=[First])

    model = metamodel.model_from_str("first 45 12")
    assert type(model) is First


@pytest.mark.parametrize("filename", ["first.tx", "first_new.tx"])
def test_metaclass_relative_paths(filename):
    current_dir = os.path.dirname(__file__)
    mm = metamodel_from_file(
        os.path.join(current_dir, "test_import", "importoverride", filename)
    )
    Third = mm["Third"]
    ThirdMasked = mm["relative.third.Third"]
    assert Third is not ThirdMasked

    model = mm.model_from_str('first 12 45 third "abc" "xyz"')
    inner_second = model.first[0]

    assert all(type(x) is ThirdMasked for x in inner_second.second)
    assert all(type(x) is Third for x in model.third)


def test_diamond_import():
    """
    Test that diamond rule import results in the same class.
    """

    current_dir = os.path.dirname(__file__)
    mm = metamodel_from_file(
        os.path.join(current_dir, "test_import", "importoverride", "first_diamond.tx")
    )
    First = mm["First"]
    MyDiamondRule = mm["diamond.last.MyDiamondRule"]

    model = mm.model_from_str("second 12 45 third 4 5")

    assert type(model) is First
    assert all(type(x.diamond) is MyDiamondRule for x in model.seconds)
    assert all(type(x.diamond) is MyDiamondRule for x in model.thirds)
