from pytest import raises

from textx import metamodel_from_str
from textx.scoping.tools import get_unique_named_object

metamodel_str = r"""
Model:
    access+=Access
;
Access:
    'access' name=ID pyobj=[OBJECT] ('.' pyattr=[OBJECT])?
;
Comment: /\/\/.*$/;
"""


def test_reference_to_buildin_attribute():
    # This test demonstrates how to link a textX model to
    # an arbitrary other non textX model.
    #
    # "foreign_model" be an arbitrary object, e.g., a AST from another
    # (non textX) meta model.
    # We can (in combination with a special scope provider)
    # reference (and combine) our textX model with this model from
    # the (non textX) meta model object.
    foreign_model = {"name": "Test", "value": 3}

    # custom scope provider
    def my_scope_provider(obj, attr, attr_ref):
        pyobj = obj.pyobj
        if attr_ref.obj_name in pyobj:
            return pyobj[attr_ref.obj_name]
        else:
            raise Exception(f"{attr_ref.obj_name} not found")

    # create meta model
    my_metamodel = metamodel_from_str(
        metamodel_str, builtins={"foreign_model": foreign_model}
    )
    my_metamodel.register_scope_providers(
        {
            "Access.pyattr": my_scope_provider,
        }
    )

    # read model
    my_model = my_metamodel.model_from_str(
        """
    access A1 foreign_model
    access A2 foreign_model.name
    access A3 foreign_model.value
    """
    )

    # check that the references are OK
    A2_name = get_unique_named_object(my_model, "A2").pyattr
    assert A2_name is foreign_model["name"]
    A3_val = get_unique_named_object(my_model, "A3").pyattr
    assert A3_val is foreign_model["value"]

    # check error cases
    with raises(Exception, match=r".*noname not found.*"):
        my_metamodel.model_from_str(
            """
        access A1 foreign_model
        access A2 foreign_model.noname
        """
        )

    with raises(Exception, match=r".*unknown_model.*"):
        my_metamodel.model_from_str(
            """
        access A1 foreign_model
        access A2 unknown_model.name
        """
        )
    with raises(Exception, match=r".*unknown_model.*"):
        my_metamodel.model_from_str(
            """
        access A1 unknown_model
        access A2 foreign_model.name
        """
        )

    pass
