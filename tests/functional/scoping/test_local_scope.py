from textx.metamodel import metamodel_from_file
import textx.scoping as scoping
from os.path import dirname, abspath
import textx.exceptions
from pytest import raises


def test_postponed_resolution_error():
    #################################
    # META MODEL DEF
    #################################

    def from_port(parser, obj, attr, obj_ref):
        return scoping.Postponed()
    def to_port(parser, obj, attr, obj_ref):
        return scoping.Postponed()

    my_meta_model = metamodel_from_file(abspath(dirname(__file__)) + '/components_model1/Components.tx')
    my_meta_model.register_scope_provider({
        "*.*":scoping.scope_provider_fully_qualified_names,
        "Connection.from_port":from_port,
        "Connection.to_port":to_port
    })

    #################################
    # MODEL PARSING
    #################################

    with raises(textx.exceptions.TextXSemanticError, match=r'.*Unresolvable cross references.*'):
        my_model = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/components_model1/example.components")


def test_model_with_local_scope():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(abspath(dirname(__file__)) + '/components_model1/Components.tx')
    my_meta_model.register_scope_provider({
        "*.*":scoping.scope_provider_fully_qualified_names,
        "Connection.from_port":scoping.ScopeProviderForSimpleRelativeNamedLookups("from.component","slots"),
        "Connection.to_port":scoping.ScopeProviderForSimpleRelativeNamedLookups("to.component","slots")
    })


    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/components_model1/example.components")

    #################################
    # TEST MODEL
    #################################

    # TODO

    #################################
    # END
    #################################

def test_model_with_local_scope_postponed():
    #################################
    # META MODEL DEF
    #################################

    sp1 = scoping.ScopeProviderForSimpleRelativeNamedLookups("from.component","slots")
    my_meta_model1 = metamodel_from_file(abspath(dirname(__file__)) + '/components_model1/Components.tx')
    my_meta_model1.register_scope_provider({
        "*.*":scoping.scope_provider_fully_qualified_names,
        "Connection.from_port":sp1,
        "Connection.to_port":scoping.ScopeProviderForSimpleRelativeNamedLookups("to.component","slots")
    })

    sp2 = scoping.ScopeProviderForSimpleRelativeNamedLookups("from.component","slots")
    my_meta_model2 = metamodel_from_file(abspath(dirname(__file__)) + '/components_model2/Components.tx')
    my_meta_model2.register_scope_provider({
        "*.*":scoping.scope_provider_fully_qualified_names,
        "Connection.from_port":sp2,
        "Connection.to_port":scoping.ScopeProviderForSimpleRelativeNamedLookups("to.component","slots")
    })


    #################################
    # MODEL PARSING
    #################################

    my_model1 = my_meta_model1.model_from_file(abspath(dirname(__file__)) + "/components_model1/example.components")
    my_model2 = my_meta_model2.model_from_file(abspath(dirname(__file__)) + "/components_model2/example.components")

    #################################
    # TEST MODEL
    #################################

    assert sp1.postponed_counter>0 or sp2.postponed_counter>0

    #################################
    # END
    #################################
