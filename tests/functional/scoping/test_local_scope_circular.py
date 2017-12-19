from textx.metamodel import metamodel_from_file
from textx.model import children_of_type
import textx.scoping as scoping
from os.path import dirname, abspath
import textx.exceptions
from pytest import raises
from tests.functional.scoping.test_import_module import get_unique_named_object

def test_model_with_local_scope_and_circular_ref_via_two_models():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(abspath(dirname(__file__)) + '/components_model1/Components.tx', enable_global_model_repository=True)
    global_scope = scoping.ScopeProviderPlainNamesWithGlobalRepo( abspath(dirname(__file__)) + "/components_model1/example_*.components")
    my_meta_model.register_scope_provider({
        "*.*":global_scope,
        "Connection.from_port":scoping.ScopeProviderForSimpleRelativeNamedLookups("from_inst.component","slots"),
        "Connection.to_port":scoping.ScopeProviderForSimpleRelativeNamedLookups("to_inst.component","slots")
    })


    #################################
    # MODEL PARSING
    #################################

    #my_modelA = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/components_model1/example_A.components")

    #################################
    # TEST MODEL
    #################################

    #################################
    # END
    #################################
