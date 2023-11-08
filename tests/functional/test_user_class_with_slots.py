import pytest  # noqa
from textx import metamodel_from_str

grammar = """
Shape:
    'shape'
    points+=Point
    'end'
;
Point:
    'point' x=INT y=INT
;
"""


def test_user_class_with_slots():
    """
    User supplied meta class.
    """

    class Point:
        "User class."

        __slots__ = ["parent", "x", "y"]

        def __init__(self, parent, x, y):
            self.parent = parent
            self.x = x
            self.y = y

    modelstr = """
    shape
    point 34 45
    point 12 23
    end
    """

    mm = metamodel_from_str(grammar, classes=[Point], auto_init_attributes=False)
    model = mm.model_from_str(modelstr)
    # Test that user class is instantiated
    point = model.points[0]

    assert type(point).__name__ == "Point"
    assert type(point) is Point

    assert len(model.points) == 2
    assert point.x == 34
    assert point.y == 45
