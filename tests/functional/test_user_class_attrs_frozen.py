from dataclasses import dataclass

import pytest  # noqa

from textx import metamodel_from_str


@pytest.mark.parametrize("frozen", [False, True])
def test_user_class_attrs(frozen):
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

    modelstr = """
    A something
    B a=something
    """

    @dataclass
    class A:
        parent: object
        name: object

    @dataclass(frozen=frozen)
    class B:
        parent: object
        a: object

    mm = metamodel_from_str(grammar, classes=[A, B], auto_init_attributes=False)
    model = mm.model_from_str(modelstr)
    assert model.b.a == model.a


def test_inheritance_attrs():
    grammar = """
    Document:
        super=Super
        sub=Sub
    ;
    Super:
        'Super' a=INT
    ;
    Sub:
        'Sub' a=INT b=ID
    ;
    """

    modelstr = """
    Super 1
    Sub 2 something
    """

    @dataclass
    class Super:
        parent: object
        a: object

    @dataclass
    class Sub(Super):
        b: object

    super_getattribute = Super.__getattribute__
    sub_getattribute = Sub.__getattribute__

    mm = metamodel_from_str(grammar, classes=[Super, Sub])
    model = mm.model_from_str(modelstr)
    assert model.sub.b == "something"

    # Make sure that the special methods of both classes have been correctly
    # restored
    assert Super.__getattribute__ == super_getattribute
    assert Sub.__getattribute__ == sub_getattribute
