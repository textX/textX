import pytest  # noqa
from textx import metamodel_from_str

grammar = """
First:
    'first' seconds+=Second
;

Second:
    sec=INT
;
"""


def test_user_class_init_order():
    """
    User supplied meta class.
    """

    init_order = []

    class First:
        "User class."

        def __init__(self, seconds):
            "Constructor must be without parameters."
            self.seconds = seconds
            init_order.append(self)

    class Second:
        "User class"

        def __init__(self, parent, sec):
            self.parent = parent
            self.sec = sec
            init_order.append(self)

    modelstr = """
    first 0 1 2
    """

    mm = metamodel_from_str(grammar, classes=[First, Second])
    first = mm.model_from_str(modelstr)

    expected_init_order = first.seconds + [first]
    assert init_order == expected_init_order
