"""
Testing user class constructor call and parent reference.
"""
import pytest  # noqa
from textx import metamodel_from_str
from textx.scoping.providers import PlainName


# Second objects are children of First.
# They should have a parent reference.
grammar = """
First:
    'first' seconds+=Second
    ('A' a+=INT)?
    ('B' b=BOOL)?
    ('C' c=STRING)?
;

Second:
    sec = INT
;

"""


def test_parent_reference():
    """
    Tests that nested objects will have "parent" reference
    that points to containing instance and non-nested
    objects does not have this reference.
    """
    metamodel = metamodel_from_str(grammar)

    model_str = 'first 34 45 7 A 45 65 B true C "dfdf"'
    model = metamodel.model_from_str(model_str)

    assert model.seconds
    for s in model.seconds:
        # Parent reference for each Second instance
        # reffers to the root First instance.
        assert s.parent == model

    # First is not nested so it should not have a parent
    # attribute
    assert not hasattr(model, "parent")


def test_user_class_constructor_call():
    """
    Tests that user class constructor gets called and
    that parent reference is given in the parameters.
    """

    class Second:
        _called = False

        def __init__(self, parent, sec):
            self._called = True
            self.parent = parent
            self.sec = sec

    metamodel = metamodel_from_str(grammar, classes=[Second])

    model_str = 'first 34 45 7 A 45 65 B true C "dfdf"'
    model = metamodel.model_from_str(model_str)

    assert model.seconds
    for s in model.seconds:
        assert s._called
        assert s.parent == model
        assert s.sec in [34, 45, 7]


def test_user_class_pass_to_constructor_only_metamodel_defined_attrs():
    """
    Test that additional attributes can be created during model loading and
    that those additional attributes are not passed to the constructor.  Only
    meta-model defined attributes should be passed to the user-class
    constructor.
    """
    grammar = r"""
    Model: elements*=Element refs*=Reference;
    Element: 'E' name=ID;
    Reference: 'ref' ref=[Element];
    """

    class Element:
        _called = False

        def __init__(self, parent, name):
            Element._called = True
            self.parent = parent
            self.name = name

    scope_provider_called = [False]

    def my_scope_provider(obj, attr, obj_ref):
        scope_provider_called[0] = True
        obj.some_new_attr = True
        # Delegate to plain name scoping provider
        return PlainName()(obj, attr, obj_ref)

    metamodel = metamodel_from_str(grammar, classes=[Element])
    metamodel.register_scope_providers({"Reference.ref": my_scope_provider})

    model_str = r"""
    E first E second
    ref second
    """
    model = metamodel.model_from_str(model_str)

    assert scope_provider_called[0]
    assert Element._called
    # Verify that attribute attached from scope provider exists
    assert model.refs[0].some_new_attr
