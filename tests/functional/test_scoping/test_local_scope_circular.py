from __future__ import unicode_literals
from textx import metamodel_from_file
from textx import get_children_of_type
import textx.scoping as scoping
from os.path import dirname, abspath
from textx.scoping_tools import get_unique_named_object


def test_model_with_local_scope_and_circular_ref_via_two_models():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(abspath(dirname(__file__)) + '/components_model1/Components.tx',
                                        global_repository=True)
    global_scope = scoping.ScopeProviderFullyQualifiedNamesWithGlobalRepo(
        abspath(dirname(__file__)) + "/components_model1/example_?.components")
    my_meta_model.register_scope_providers({
        "*.*": global_scope,
        "Connection.from_port": scoping.ScopeProviderForSimpleRelativeNamedLookups("from_inst.component.slots"),
        "Connection.to_port": scoping.ScopeProviderForSimpleRelativeNamedLookups("to_inst.component.slots")
    })

    #################################
    # MODEL PARSING
    #################################

    my_model_a = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/components_model1/example_A.components")
    my_model_b = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/components_model1/example_B.components")

    a_my_a = get_unique_named_object(my_model_a, "mya")
    a_my_b = get_unique_named_object(my_model_a, "myb")
    b_my_a = get_unique_named_object(my_model_b, "mya")
    b_my_b = get_unique_named_object(my_model_b, "myb")

    assert a_my_a != b_my_a
    assert a_my_b != b_my_b

    assert a_my_a.component == b_my_a.component  # same component "class"
    assert a_my_b.component == b_my_b.component  # same component "class"

    a_connections = get_children_of_type("Connection", my_model_a)
    b_connections = get_children_of_type("Connection", my_model_b)

    a_connection = list(filter(lambda x: x.from_inst == a_my_a and x.to_inst == a_my_b, a_connections))
    b_connection = list(filter(lambda x: x.from_inst == b_my_a and x.to_inst == b_my_b, b_connections))
    assert len(a_connection) == 1
    assert len(b_connection) == 1

    #################################
    # TEST MODEL
    #################################

    #################################
    # END
    #################################
