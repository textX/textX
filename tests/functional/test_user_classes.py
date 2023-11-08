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

    class First:
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
                assert hasattr(second, "sec") and isinstance(second.sec, int)

    class Second:
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
    assert not isinstance(model, First)

    mm = metamodel_from_str(grammar, classes=[First, Second])
    model = mm.model_from_str(modelstr)
    # Test that user class is instantiated
    assert type(model).__name__ == "First"
    assert isinstance(model, First)
    # Check default attributes
    assert isinstance(model.a, list)
    assert model.a == []
    assert isinstance(model.b, bool)
    assert model.b is False

    # Check additional attributes
    assert model.some_attr == 1


class Thing:
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])


class AThing:
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])


class BThing:
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])


def test_user_class_with_imported_grammar():
    this_folder = dirname(abspath(__file__))
    mm = metamodel_from_file(
        join(this_folder, "user_classes", "B.tx"), classes=[AThing, BThing]
    )
    called = [False]

    def dummy(_):
        called[0] = True

    mm.register_obj_processors({"AThing": dummy})
    m = mm.model_from_str(
        """
        A 2,1
        B Hello
    """
    )
    assert called[0]
    assert m.a.v.x == 2
    assert m.a.v.y == 1
    assert m.b.v.name == "Hello"
    assert type(m.b.v).__name__ == "Thing"
    assert type(m.a.v).__name__ == "Thing"
    assert isinstance(m.a, AThing)
    assert isinstance(m.b, BThing)

    with raises(
        TextXSemanticError,
        match=r".*redefined imported rule Thing"
        + r" cannot be replaced by a user class.*",
    ):
        mm = metamodel_from_file(
            join(this_folder, "user_classes", "B.tx"), classes=[AThing, BThing, Thing]
        )
    # now, all involved user classes **may** be instrumented...
    # (after an exception, we do not guarantee 100% cleanup of user classes)
