from textx.metamodel import metamodel_from_file
from textx.model import children_of_type
import textx.scoping as scoping
from os.path import dirname, abspath
import textx.exceptions
from pytest import raises
from tests.functional.scoping.test_import_module import get_unique_named_object

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
        "Connection.from_port":scoping.ScopeProviderForSimpleRelativeNamedLookups("from_inst.component","slots"),
        "Connection.to_port":scoping.ScopeProviderForSimpleRelativeNamedLookups("to_inst.component","slots")
    })


    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/components_model1/example.components")

    #################################
    # TEST MODEL
    #################################

    # test local refs
    action2 = get_unique_named_object(my_model, "action2")
    action3 = get_unique_named_object(my_model, "action3")
    connections = children_of_type("Connection",my_model)
    selected_connections = list(filter(lambda x:x.from_inst==action2 and x.to_inst==action3, connections))
    assert len(selected_connections)==1

    # test list of formats
    input2 = get_unique_named_object(my_model, "input2")
    assert len(input2.formats)==3
    format_names = map( lambda x:x.name, input2.formats )
    assert "A" in format_names
    assert "B" in format_names
    assert "C" in format_names
    assert not "D" in format_names

    #################################
    # END
    #################################

def test_model_with_local_scope_postponed():
    #################################
    # META MODEL DEF
    #################################

    sp1 = scoping.ScopeProviderForSimpleRelativeNamedLookups("from_inst.component","slots")
    my_meta_model1 = metamodel_from_file(abspath(dirname(__file__)) + '/components_model1/Components.tx')
    my_meta_model1.register_scope_provider({
        "*.*":scoping.scope_provider_fully_qualified_names,
        "Connection.from_port":sp1,
        "Connection.to_port":scoping.ScopeProviderForSimpleRelativeNamedLookups("to_inst.component","slots")
    })

    sp2 = scoping.ScopeProviderForSimpleRelativeNamedLookups("from_inst.component","slots")
    my_meta_model2 = metamodel_from_file(abspath(dirname(__file__)) + '/components_model2/Components.tx')
    my_meta_model2.register_scope_provider({
        "*.*":scoping.scope_provider_fully_qualified_names,
        "Connection.from_port":sp2,
        "Connection.to_port":scoping.ScopeProviderForSimpleRelativeNamedLookups("to_inst.component","slots")
    })


    #################################
    # MODEL PARSING
    #################################

    _ = my_meta_model1.model_from_file(abspath(dirname(__file__)) + "/components_model1/example.components")
    _ = my_meta_model2.model_from_file(abspath(dirname(__file__)) + "/components_model2/example.components")

    #################################
    # TEST MODEL
    #################################

    assert sp1.postponed_counter>0 or sp2.postponed_counter>0

    #################################
    # END
    #################################
