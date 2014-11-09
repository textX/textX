import pytest
from textx.metamodel import metamodel_from_str

grammar = """
First:
    'first' seconds+=Second
    ('A' a+=INT)?
    ('B' b=BOOL)?
    ('C' c=STRING)?
;

Second:
    INT|STRING
;

"""

def test_user_class():
    """
    User supplied meta class.
    """
    class First(object):
        "User class."
        def __init__(self):
            "Constructor must be without parameters."
            # Testing that additional attributes
            # are preserved.
            self.some_attr = 1


    modelstr = """
    first 34 45 65 "sdf" 45
    """

    mm = metamodel_from_str(grammar)
    model = mm.model_from_str(modelstr)
    # Test that generic First class is created
    assert type(model).__name__ == "First"
    assert type(model) is not First

    mm = metamodel_from_str(grammar, classes=[First])
    model = mm.model_from_str(modelstr)
    # Test that user class is instantiated
    assert type(model).__name__ == "First"
    assert type(model) is First
    # Check default attributes
    assert type(model.a) is list
    assert model.a == []
    assert type(model.b) is bool
    assert model.b == False

    # Check additional attributes
    assert model.some_attr == 1

