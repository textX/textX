from pytest import raises

from textx.metamodel import wrap_attrs, AttrsWrapper, WrappingError


def test_wrap_attrs():
    class TestClass(object):
        _tx_attrs = []

    obj = TestClass()
    wrapped = wrap_attrs(obj)
    assert isinstance(wrapped, AttrsWrapper)

    with raises(WrappingError):
        type(wrapped) == object

    with raises(WrappingError):
        object == type(wrapped)

    with raises(WrappingError):
        wrapped.__class__

    with raises(WrappingError):
        wrapped.__dict__

