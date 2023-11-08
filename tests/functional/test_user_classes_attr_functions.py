import pytest  # noqa
from textx import metamodel_from_str

grammar = r"""
A: 'A' x=INT b=B c=C;
B: 'B' x=INT;
C: 'C' x=INT;
"""

modelstr = r"""
A 1 B 2 C 3
"""


class A:
    """
    A defines a class with a custom setattr method
    (it stores the __setattr__ in its __dict__).
    """

    def __init__(self, **kwargs):
        super().__init__()
        for k, v in kwargs.items():
            self.__dict__[k] = v

    def __setattr__(self, name, value):
        pass


class B(A):
    """
    B defines a class inheriting the custom setattr method from A
    (it does not store the __setattr__ in its __dict__).
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class C(B):
    """
    A defines a class with a custom setattr method
    It overrides the __setattr__ from B/A.
    (it stores its own __setattr__ in its __dict__).
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        pass


def test_user_class_attr_functions_are_restored_correctly():
    """
    User supplied meta class.
    Documentation of correct handling of custom attr methods.
    """

    origA = A.__dict__["__setattr__"]
    assert "__setattr__" not in B.__dict__
    origC = C.__dict__["__setattr__"]

    assert origA is not None
    assert origC is not None

    mm = metamodel_from_str(grammar, classes=[A, B, C])
    _ = mm.model_from_str(modelstr)

    assert origA is A.__dict__["__setattr__"]
    assert "__setattr__" not in B.__dict__
    assert origC is C.__dict__["__setattr__"]

    mm = metamodel_from_str(grammar, classes=[C, B, A])
    _ = mm.model_from_str(modelstr)

    assert origA is A.__dict__["__setattr__"]
    assert "__setattr__" not in B.__dict__
    assert origC is C.__dict__["__setattr__"]
