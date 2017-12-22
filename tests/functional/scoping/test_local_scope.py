from __future__ import unicode_literals

from textx import metamodel_from_file
from textx import children_of_type
import textx.scoping as scoping
from textx.scoping_tools import get_unique_named_object

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
        "Connection.from_port":scoping.ScopeProviderForSimpleRelativeNamedLookups("from_inst.component.slots"),
        "Connection.to_port":scoping.ScopeProviderForSimpleRelativeNamedLookups("to_inst.component.slots")
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

def test_model_with_local_scope_and_error():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(abspath(dirname(__file__)) + '/components_model1/Components.tx')
    my_meta_model.register_scope_provider({
        "*.*":scoping.scope_provider_fully_qualified_names,
        "Connection.from_port":scoping.ScopeProviderForSimpleRelativeNamedLookups("from_inst.component.slots"),
        "Connection.to_port":scoping.ScopeProviderForSimpleRelativeNamedLookups("to_inst.component.slots")
    })

    #################################
    # MODEL PARSING
    #################################

    with raises(textx.exceptions.TextXSemanticError, match=r'.*Unknown objec.*input1.*SlotIn.*'):
        my_model = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/components_model1/example_err1.components")

    #################################
    # END
    #################################


def test_model_with_local_scope_and_inheritance2():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(abspath(dirname(__file__)) + '/components_model1/Components.tx')
    my_meta_model.register_scope_provider({
        "*.*":scoping.scope_provider_fully_qualified_names,
        "Connection.from_port":scoping.ScopeProviderForExtendableRelativeNamedLookups("from_inst.component","slots","extends"),
        "Connection.to_port":scoping.ScopeProviderForExtendableRelativeNamedLookups("to_inst.component","slots","extends")
    })

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/components_model1/example_inherit1.components")

    #################################
    # TEST MODEL
    #################################

    # test inherited ports are same (direct inheritance)
    action1 = get_unique_named_object(my_model, "action1")
    action2 = get_unique_named_object(my_model, "action2")
    action3 = get_unique_named_object(my_model, "action3")
    end     = get_unique_named_object(my_model, "end")
    connections = children_of_type("Connection",my_model)
    selected_connections_12 = list(filter(lambda x:x.from_inst==action1 and x.to_inst==action2, connections))
    selected_connections_3e = list(filter(lambda x:x.from_inst==action3 and x.to_inst==end, connections))
    assert len(selected_connections_12)==1
    assert len(selected_connections_3e)==1
    assert selected_connections_12[0].to_port is selected_connections_3e[0].to_port # output3 is same

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/components_model1/example_inherit2.components")

    #################################
    # TEST MODEL
    #################################

    # test inherited ports are same (indirect inheritance: Middle -> Start -> End)
    action1 = get_unique_named_object(my_model, "action1")
    action2 = get_unique_named_object(my_model, "action2")
    action3 = get_unique_named_object(my_model, "action3")
    end     = get_unique_named_object(my_model, "end")
    connections = children_of_type("Connection",my_model)
    selected_connections_12 = list(filter(lambda x:x.from_inst==action1 and x.to_inst==action2, connections))
    selected_connections_3e = list(filter(lambda x:x.from_inst==action3 and x.to_inst==end, connections))
    assert len(selected_connections_12)==1
    assert len(selected_connections_3e)==1
    assert selected_connections_12[0].to_port is selected_connections_3e[0].to_port # output3 is same


    #################################
    # END
    #################################


def test_model_with_local_scope_postponed():
    #################################
    # META MODEL DEF
    #################################

    sp1 = scoping.ScopeProviderForSimpleRelativeNamedLookups("from_inst.component.slots")
    my_meta_model1 = metamodel_from_file(abspath(dirname(__file__)) + '/components_model1/Components.tx')
    my_meta_model1.register_scope_provider({
        "*.*":scoping.scope_provider_fully_qualified_names,
        "Connection.from_port":sp1,
        "Connection.to_port":scoping.ScopeProviderForSimpleRelativeNamedLookups("to_inst.component.slots")
    })

    sp2 = scoping.ScopeProviderForSimpleRelativeNamedLookups("from_inst.component.slots")
    my_meta_model2 = metamodel_from_file(abspath(dirname(__file__)) + '/components_model2/Components.tx')
    my_meta_model2.register_scope_provider({
        "*.*":scoping.scope_provider_fully_qualified_names,
        "Connection.from_port":sp2,
        "Connection.to_port":scoping.ScopeProviderForSimpleRelativeNamedLookups("to_inst.component.slots")
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
