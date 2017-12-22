from textx import metamodel_from_file
import textx.scoping as scoping
from textx.scoping_tools import get_unique_named_object
from textx.scoping_tools import get_referenced_object, get_list_of_concatenated_objects
from os.path import dirname, abspath

def test_get_referenced_object():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(abspath(dirname(__file__)) + '/components_model1/Components.tx')
    my_meta_model.register_scope_provider({
        "*.*":scoping.scope_provider_fully_qualified_names,
        "Connection.from_port":scoping.ScopeProviderForExtendableRelativeNamedLookups("from_inst.component","slots","extends"),
        "Connection.to_port":scoping.ScopeProviderForExtendableRelativeNamedLookups("to_inst.component","slots","extends"),
    })

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/components_model1/example_inherit2.components")

    #################################
    # TEST MODEL
    #################################

    action2a = get_referenced_object(None, my_model, "packages.usage.instances.action2")
    action2b = get_unique_named_object(my_model, "action2")
    assert action2a is action2b

    Middle_a = get_referenced_object(None, my_model, "packages.base.components.Middle")
    Middle_b = get_unique_named_object(my_model, "Middle")
    assert Middle_a is Middle_b

def test_get_list_of_concatenated_objects():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(abspath(dirname(__file__)) + '/components_model1/Components.tx')
    my_meta_model.register_scope_provider({
        "*.*":scoping.scope_provider_fully_qualified_names,
        "Connection.from_port":scoping.ScopeProviderForExtendableRelativeNamedLookups("from_inst.component","slots","extends"),
        "Connection.to_port":scoping.ScopeProviderForExtendableRelativeNamedLookups("to_inst.component","slots","extends"),
    })

    #################################
    # MODEL PARSING
    #################################

    my_model1 = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/components_model1/example_inherit1.components")
    my_model2 = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/components_model1/example_inherit2.components")

    #################################
    # TEST MODEL
    #################################

    # test extends A,B
    Start  = get_unique_named_object(my_model1, "Start")
    Middle = get_unique_named_object(my_model1, "Middle")
    End    = get_unique_named_object(my_model1, "End")
    inherited_classes = get_list_of_concatenated_objects(Middle, "extends")
    assert len(inherited_classes)==3
    assert inherited_classes[0] is Middle
    assert inherited_classes[1] is Start
    assert inherited_classes[2] is End

    # test extends A extends B
    Start  = get_unique_named_object(my_model2, "Start")
    Middle = get_unique_named_object(my_model2, "Middle")
    End    = get_unique_named_object(my_model2, "End")
    inherited_classes = get_list_of_concatenated_objects(Middle, "extends")
    assert len(inherited_classes)==3
    assert inherited_classes[0] is Middle
    assert inherited_classes[1] is Start
    assert inherited_classes[2] is End
