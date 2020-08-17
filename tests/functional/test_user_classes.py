from __future__ import unicode_literals
import pytest  # noqa
from textx import metamodel_from_str, metamodel_from_file
from os.path import join, dirname, abspath
from pytest import raises
from textx.exceptions import TextXSemanticError


grammar = """
First:
    'first' seconds+=Second
    ('A' a+=INT)?
    ('B' b=BOOL)?
    ('C' c=STRING)?
;

Second:
    sec=INT|STRING
;

"""


def test_user_class():
    """
    User supplied meta class.
    """

    class First(object):
        "User class."
        def __init__(self, seconds, a, b, c):
            "Constructor must be without parameters."
            # Testing that additional attributes
            # are preserved.
            self.some_attr = 1
            self.seconds = seconds
            self.a = a
            self.b = b
            self.c = c

            for second in self.seconds:
                # Make sure seconds have already been instantiated
                assert hasattr(second, 'sec') and isinstance(second.sec, int)

    class Second(object):
        "User class"
        def __init__(self, parent, sec):
            self.parent = parent
            self.sec = sec

    modelstr = """
    first 34 45 65 "sdf" 45
    """

    mm = metamodel_from_str(grammar)
    model = mm.model_from_str(modelstr)
    # Test that generic First class is created
    assert type(model).__name__ == "First"
    assert type(model) is not First

    mm = metamodel_from_str(grammar, classes=[First, Second])
    model = mm.model_from_str(modelstr)
    # Test that user class is instantiated
    assert type(model).__name__ == "First"
    assert type(model) is First
    # Check default attributes
    assert type(model.a) is list
    assert model.a == []
    assert type(model.b) is bool
    assert model.b is False

    # Check additional attributes
    assert model.some_attr == 1


class Thing(object):
    def __init__(self, **kwargs):
        for k in kwargs.keys():
            setattr(self, k, kwargs[k])


class AThing(object):
    def __init__(self, **kwargs):
        for k in kwargs.keys():
            setattr(self, k, kwargs[k])


class BThing(object):
    def __init__(self, **kwargs):
        for k in kwargs.keys():
            setattr(self, k, kwargs[k])


def test_user_class_with_imported_grammar():
    this_folder = dirname(abspath(__file__))
    mm = metamodel_from_file(join(this_folder, "user_classes", "B.tx"),
                             classes=[AThing, BThing])
    m = mm.model_from_str("""
        A 2,1
        B Hello
    """)
    assert m.a.v.x == 2
    assert m.a.v.y == 1
    assert m.b.v.name == "Hello"
    assert type(m.b.v).__name__ == "Thing"
    assert type(m.a.v).__name__ == "Thing"
    assert isinstance(m.a, AThing)
    assert isinstance(m.b, BThing)

    # required, because _tx_obj_attrs is bot cleaned up:
    delattr(AThing, "_tx_obj_attrs")
    delattr(BThing, "_tx_obj_attrs")

    with raises(TextXSemanticError, match=r'.*redefined imported rule Thing cannot be replaced by a user class.*'):
        mm = metamodel_from_file(join(this_folder, "user_classes", "B.tx"),
                                 classes=[AThing, BThing, Thing])
    # now, all involved user classes **may** be instrumented... TODO
