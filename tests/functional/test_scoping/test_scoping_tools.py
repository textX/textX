from __future__ import unicode_literals
from os.path import dirname, abspath, join

import textx.scoping.providers as scoping_providers
from textx import metamodel_from_file, metamodel_from_str
from textx.scoping.tools import resolved_model_path,\
    get_list_of_concatenated_objects
from textx.scoping.tools import get_unique_named_object
from textx import textx_isinstance
from textx import get_children_of_type
from pytest import raises

def test_textx_isinstace():
    grammar = \
        '''
    Model: a=A;
    A: B;
    B: C;
    C: x=ID;
    '''
    my_meta_model = metamodel_from_str(grammar)
    A = my_meta_model['A']
    B = my_meta_model['B']
    C = my_meta_model['C']
    my_model = my_meta_model.model_from_str("c")
    c = get_children_of_type("C", my_model)
    assert len(c) == 1
    c = c[0]
    assert textx_isinstance(c, C)
    assert textx_isinstance(c, B)
    assert textx_isinstance(c, A)


def test_resolved_model_path_with_lists():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)),
             'components_model1', 'Components.tx'))
    my_meta_model.register_scope_providers({
        "*.*": scoping_providers.FQN(),
        "Connection.from_port":
            scoping_providers.ExtRelativeName("from_inst.component",
                                              "slots",
                                              "extends"),
        "Connection.to_port":
            scoping_providers.ExtRelativeName("to_inst.component",
                                              "slots",
                                              "extends"),
    })

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(
        join(abspath(dirname(__file__)),
             "components_model1", "example_inherit2.components"))

    #################################
    # TEST MODEL
    #################################

    action2a = resolved_model_path(my_model,
                                     "packages.usage.instances.action2",
                                   True)
    action2b = get_unique_named_object(my_model, "action2")
    assert action2a is action2b

    middle_a = resolved_model_path(my_model,
                                     "packages.base.components.Middle",
                                   True)
    middle_b = get_unique_named_object(my_model, "Middle")
    assert middle_a is middle_b

    action2a_with_parent = resolved_model_path(
        action2a, "parent(Model).packages.usage.instances.action2", True)
    assert action2a_with_parent == action2a

    with raises(Exception, match=r'.*unexpected: got list in path for get_referenced_object.*'):
        resolved_model_path(my_model,
                            "packages.usage.instances.action2",
                            False)


def test_resolved_model_path_simple_case():
    #################################
    # META MODEL DEF
    #################################

    grammar = r'''
        Model: name=ID a=A b=B;
        A: 'A:' name=ID;
        B: 'B:' name=ID ('->' b=B| '=' a=A );
    '''

    mm = metamodel_from_str(grammar)

    #################################
    # MODEL PARSING
    #################################

    model = mm.model_from_str(r'''
        My_Model 
            A: OuterA
            B: Level0_B
             -> B: Level1_B
             -> B: Level2_B
             = A: InnerA
    ''')

    #################################
    # TEST MODEL
    #################################

    outerA = resolved_model_path(model, "a")
    assert outerA.name == "OuterA"
    level0B = resolved_model_path(model, "b")
    assert level0B.name == "Level0_B"
    level1B = resolved_model_path(model, "b.b")
    assert level1B.name == "Level1_B"
    level2B = resolved_model_path(model, "b.b.b")
    assert level2B.name == "Level2_B"
    innerA = resolved_model_path(model, "b.b.b.a")
    assert innerA.name == "InnerA"
    outerA2 = resolved_model_path(model, "b.b.b.parent(Model).a")
    assert outerA2 == outerA

    level3B_none = resolved_model_path(model, "b.b.b.b")
    assert level3B_none is None
    innerA_none1 = resolved_model_path(model, "b.b.b.b.a")
    assert innerA_none1 is None
    innerA_none2 = resolved_model_path(model, "b.b.a")
    assert innerA_none2 is None


def test_resolved_model_path_simple_case_with_refs():
    #################################
    # META MODEL DEF
    #################################

    grammar = r'''
        Model: name=ID b=B;
        B: 'B:' name=ID ('->' b=B | '-->' bref=[B] );
    '''

    mm = metamodel_from_str(grammar)

    #################################
    # MODEL PARSING
    #################################

    model = mm.model_from_str(r'''
        My_Model 
            B: Level0_B
             -> B: Level1_B
             --> Level0_B
    ''')

    #################################
    # TEST MODEL
    #################################

    level0B = resolved_model_path(model, "b")
    assert level0B.name == "Level0_B"
    level1B = resolved_model_path(model, "b.b")
    assert level1B.name == "Level1_B"
    bref = resolved_model_path(model, "b.b.bref")
    assert bref.name == "Level0_B"
    assert bref == level0B


def test_get_list_of_concatenated_objects():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)),
             'components_model1', 'Components.tx'))
    my_meta_model.register_scope_providers({
        "*.*": scoping_providers.FQN(),
        "Connection.from_port":
            scoping_providers.ExtRelativeName("from_inst.component",
                                              "slots",
                                              "extends"),
        "Connection.to_port":
            scoping_providers.ExtRelativeName("to_inst.component",
                                              "slots",
                                              "extends"),
    })

    #################################
    # MODEL PARSING
    #################################

    my_model1 = my_meta_model.model_from_file(
        join(abspath(dirname(__file__)),
             "components_model1", "example_inherit1.components"))
    my_model2 = my_meta_model.model_from_file(
        join(abspath(dirname(__file__)),
             "components_model1", "example_inherit2.components"))

    #################################
    # TEST MODEL
    #################################

    # test extends A,B
    start = get_unique_named_object(my_model1, "Start")
    middle = get_unique_named_object(my_model1, "Middle")
    end = get_unique_named_object(my_model1, "End")
    inherited_classes = get_list_of_concatenated_objects(middle, "extends")
    assert len(inherited_classes) == 3
    assert inherited_classes[0] is middle
    assert inherited_classes[1] is start
    assert inherited_classes[2] is end

    # test extends A extends B
    start = get_unique_named_object(my_model2, "Start")
    middle = get_unique_named_object(my_model2, "Middle")
    end = get_unique_named_object(my_model2, "End")
    inherited_classes = get_list_of_concatenated_objects(middle, "extends")
    assert len(inherited_classes) == 3
    assert inherited_classes[0] is middle
    assert inherited_classes[1] is start
    assert inherited_classes[2] is end
