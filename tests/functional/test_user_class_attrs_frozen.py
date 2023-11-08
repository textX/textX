import pytest  # noqa
from textx import metamodel_from_str


@pytest.mark.parametrize("frozen", [False, True])
def test_user_class_attrs(frozen):
    attr = pytest.importorskip("attr")
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

    @attr.s()
    class A:
        parent = attr.ib()
        name = attr.ib()

    @attr.s(frozen=frozen)
    class B:
        parent = attr.ib()
        a = attr.ib()

    mm = metamodel_from_str(grammar, classes=[A, B], auto_init_attributes=False)
    model = mm.model_from_str(modelstr)
    assert model.b.a == model.a


def test_inheritance_attrs():
    attr = pytest.importorskip("attr")

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

    @attr.s()
    class Super:
        parent = attr.ib()
        a = attr.ib()

    @attr.s()
    class Sub(Super):
        b = attr.ib()

    super_getattribute = Super.__getattribute__
    sub_getattribute = Sub.__getattribute__

    mm = metamodel_from_str(grammar, classes=[Super, Sub])
    model = mm.model_from_str(modelstr)
    assert model.sub.b == "something"

    # Make sure that the special methods of both classes have been correctly
    # restored
    assert Super.__getattribute__ == super_getattribute
    assert Sub.__getattribute__ == sub_getattribute
