from os.path import abspath, dirname, join

from pytest import raises

from textx import metamodel_from_str
from textx.scoping.tools import get_unique_named_object

metamodel_str = r"""
Model:
    imports+=Json
    access+=Access
;
Access:
    'access' name=ID pyobj=[Json] '.' pyattr=[OBJECT]?
;

Json: 'import' filename=STRING 'as' name=ID;
Comment: /\/\/.*$/;
"""


def test_reference_to_nontextx_attribute():
    # This test demonstrates how to link a textX model to
    # an arbitrary other non textX model.
    # Here we use a json file as external model
    # to demonstrate how to load external models on the fly.

    # custom scope provider
    def generic_scope_provider(obj, attr, attr_ref):
        if not obj.pyobj:
            from textx.scoping import Postponed

            return Postponed()
        if not hasattr(obj.pyobj, "data"):
            import json

            with open(join(abspath(dirname(__file__)), obj.pyobj.filename)) as f:
                obj.pyobj.data = json.load(f)
        if attr_ref.obj_name in obj.pyobj.data:
            return obj.pyobj.data[attr_ref.obj_name]
        else:
            raise Exception(f"{attr_ref.obj_name} not found")

    # create meta model
    my_metamodel = metamodel_from_str(metamodel_str)
    my_metamodel.register_scope_providers(
        {
            "Access.pyattr": generic_scope_provider,
        }
    )

    # read model
    my_model = my_metamodel.model_from_str(
        """
    import "test_reference_to_nontextx_attribute/othermodel.json" as data
    access A1 data.name
    access A2 data.gender
    """
    )

    # check that the references are OK
    A1_name = get_unique_named_object(my_model, "A1").pyattr
    assert A1_name == "pierre"
    A2_gender = get_unique_named_object(my_model, "A2").pyattr
    assert A2_gender == "male"

    with raises(Exception, match=r".*noname.*"):
        my_metamodel.model_from_str(
            """
        import "test_reference_to_nontextx_attribute/othermodel.json" as data
        access A1 data.noname
        access A2 data.gender
        """
        )

    with raises(Exception, match=r".*filenotfound.*"):
        my_metamodel.model_from_str(
            """
        import "test_reference_to_nontextx_attribute/filenotfound.json" as data
        access A1 data.name
        access A2 data.gender
        """
        )

    pass
