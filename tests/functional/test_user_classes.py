from __future__ import unicode_literals
import pytest  # noqa
from textx import metamodel_from_str

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
