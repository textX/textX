from __future__ import unicode_literals
import pytest  # noqa
from textx import metamodel_from_str

grammar = """
Document:
    a=A
    b=B
;
A:
    'A' name=ID
;
B:
    'B' 'a' '=' a=[A]
;
"""


@pytest.mark.parametrize('frozen', [False, True])
def test_user_class_attrs(frozen):
    attr = pytest.importorskip('attr')
    """
    User supplied meta class.
    """
    @attr.s(frozen=frozen)
    class Point(object):
        "User class."
        parent = attr.ib()
        name = attr.ib()
        x = attr.ib()
        y = attr.ib()

    modelstr = """
    A something
    B a=something
    """

    @attr.s()
    class A(object):
        parent = attr.ib()
        name = attr.ib()

    @attr.s(frozen=frozen)
    class B(object):
        parent = attr.ib()
        a = attr.ib()

    mm = metamodel_from_str(grammar, classes=[A, B],
                            auto_init_attributes=False)
    model = mm.model_from_str(modelstr)
    assert model.b.a == model.a
