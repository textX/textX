from pytest import raises

from textx import metamodel_from_str
from textx.scoping.tools import get_unique_named_object

metamodel_str = r"""
Model:
    access+=Access
;
Access:
    'access' name=ID pyobj=[OBJECT] '.' pyattr=[OBJECT]?
;

Comment: /\/\/.*$/;
"""


class PythonScopeProvider:
    def __init__(self, dict_with_objects):
        self.dict_with_objects = dict_with_objects

    def __call__(self, obj, attr, attr_ref):
        if attr.name == "pyobj":
            if attr_ref.obj_name in self.dict_with_objects:
                return self.dict_with_objects[attr_ref.obj_name]
            else:
                raise Exception(f"{attr_ref.obj_name} not found")
        else:
            if not obj.pyobj:
                from textx.scoping import Postponed

                return Postponed()
            if hasattr(obj.pyobj, attr_ref.obj_name):
                return getattr(obj.pyobj, attr_ref.obj_name)
            else:
                raise Exception(f"{attr_ref.obj_name} not found")


def test_reference_to_python_attribute():
    # This test demonstrates how to link python objects to
    # a textX model.
    # "access" objects access python attributes.

    from collections import namedtuple

    Person = namedtuple("Person", "first_name last_name zip_code")
    p1 = Person("Tim", "Foo", 123)
    p2 = Person("Tom", "Bar", 456)

    sp = PythonScopeProvider({"p1": p1, "p2": p2})

    # create meta model
    my_metamodel = metamodel_from_str(metamodel_str)
    my_metamodel.register_scope_providers({"Access.pyobj": sp, "Access.pyattr": sp})

    # read model
    my_model = my_metamodel.model_from_str(
        """
    access A_Tim p1.first_name
    access A_123 p1.zip_code
    access A_456 p2.zip_code
    """
    )

    # check that the references are OK
    A_Tim = get_unique_named_object(my_model, "A_Tim").pyattr
    assert A_Tim == "Tim"
    A_123 = get_unique_named_object(my_model, "A_123").pyattr
    assert A_123 == 123
    A_456 = get_unique_named_object(my_model, "A_456").pyattr
    assert A_456 == 456

    with raises(Exception, match=r".*unknown.*"):
        my_metamodel.model_from_str(
            """
        access A1 p1.unknown
        """
        )

    with raises(Exception, match=r".*p3.*"):
        my_metamodel.model_from_str(
            """
        access A1 p3.first_anme
        """
        )

    pass
