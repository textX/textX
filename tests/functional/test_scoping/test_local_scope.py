from os.path import abspath, dirname, join

from pytest import raises

import textx.exceptions
import textx.scoping as scoping
import textx.scoping.providers as scoping_providers
from textx import get_children_of_type, metamodel_from_file
from textx.scoping.tools import get_unique_named_object


def test_postponed_resolution_error():
    """
    This test checks that an unresolvable scopre provider induces an exception.
    This is checked by using a scope provider which always returns a postponed
    object.
    """
    #################################
    # META MODEL DEF
    #################################

    def from_port(obj, attr, obj_ref):
        return scoping.Postponed()

    def to_port(obj, attr, obj_ref):
        return scoping.Postponed()

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "components_model1", "Components.tx")
    )
    my_meta_model.register_scope_providers(
        {
            "*.*": scoping_providers.FQN(),
            "Connection.from_port": from_port,
            "Connection.to_port": to_port,
        }
    )

    #################################
    # MODEL PARSING
    #################################

    with raises(
        textx.exceptions.TextXSemanticError, match=r".*Unresolvable cross references.*"
    ):
        my_meta_model.model_from_file(
            join(abspath(dirname(__file__)), "components_model1", "example.components")
        )


def test_model_with_local_scope():
    """
    This is a basic test for the local scope provider (good case).
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "components_model1", "Components.tx")
    )
    my_meta_model.register_scope_providers(
        {
            "*.*": scoping_providers.FQN(),
            "Connection.from_port": scoping_providers.RelativeName(
                "from_inst.component.slots"
            ),
            "Connection.to_port": scoping_providers.RelativeName(
                "to_inst.component.slots"
            ),
        }
    )

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(
        join(abspath(dirname(__file__)), "components_model1", "example.components")
    )

    #################################
    # TEST MODEL
    #################################

    # test local refs
    action2 = get_unique_named_object(my_model, "action2")
    action3 = get_unique_named_object(my_model, "action3")
    connections = get_children_of_type("Connection", my_model)
    selected_connections = list(
        filter(lambda x: x.from_inst == action2 and x.to_inst == action3, connections)
    )
    assert len(selected_connections) == 1

    # test list of formats
    input2 = get_unique_named_object(my_model, "input2")
    assert len(input2.formats) == 3
    format_names = map(lambda x: x.name, input2.formats)
    assert "A" in format_names
    assert "B" in format_names
    assert "C" in format_names
    assert "D" not in format_names

    #################################
    # END
    #################################


def test_model_with_local_scope_and_error():
    """
    This is a basic test for the local scope provider (bad case).
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "components_model1", "Components.tx")
    )
    my_meta_model.register_scope_providers(
        {
            "*.*": scoping_providers.FQN(),
            "Connection.from_port": scoping_providers.RelativeName(
                "from_inst.component.slots"
            ),
            "Connection.to_port": scoping_providers.RelativeName(
                "to_inst.component.slots"
            ),
        }
    )

    #################################
    # MODEL PARSING
    #################################

    with raises(
        textx.exceptions.TextXSemanticError, match=r".*Unknown object.*input1.*SlotIn.*"
    ):
        my_meta_model.model_from_file(
            join(
                abspath(dirname(__file__)), "components_model1", "example_err1.components"
            )
        )

    #################################
    # END
    #################################


def test_model_with_local_scope_and_error_267():
    """
    This is a basic test for the local scope provider (bad case, #267).
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "components_model1", "Components.tx")
    )
    my_meta_model.register_scope_providers(
        {
            "*.*": scoping_providers.FQN(),
            "Connection.from_port": scoping_providers.RelativeName(
                "from_inst.component.slots"
            ),
            "Connection.to_port": scoping_providers.RelativeName(
                "to_inst.component.slots"
            ),
        }
    )

    #################################
    # MODEL PARSING
    #################################

    with raises(
        textx.exceptions.TextXSemanticError, match=r".*Unknown object.*pu.*SlotOut.*"
    ):
        my_meta_model.model_from_file(
            join(
                abspath(dirname(__file__)), "components_model1", "example_err2.components"
            )
        )

    #################################
    # END
    #################################


def test_model_with_local_scope_and_inheritance2():
    """
    This is a more complicated test for the local scope provider.
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "components_model1", "Components.tx")
    )
    my_meta_model.register_scope_providers(
        {
            "*.*": scoping_providers.FQN(),
            "Connection.from_port": scoping_providers.ExtRelativeName(
                "from_inst.component", "slots", "extends"
            ),
            "Connection.to_port": scoping_providers.ExtRelativeName(
                "to_inst.component", "slots", "extends"
            ),
        }
    )

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(
        join(
            abspath(dirname(__file__)), "components_model1", "example_inherit1.components"
        )
    )

    #################################
    # TEST MODEL
    #################################

    # test inherited ports are same (direct inheritance)
    action1 = get_unique_named_object(my_model, "action1")
    action2 = get_unique_named_object(my_model, "action2")
    action3 = get_unique_named_object(my_model, "action3")
    end = get_unique_named_object(my_model, "end")
    connections = get_children_of_type("Connection", my_model)
    selected_connections_12 = list(
        filter(lambda x: x.from_inst == action1 and x.to_inst == action2, connections)
    )
    selected_connections_3e = list(
        filter(lambda x: x.from_inst == action3 and x.to_inst == end, connections)
    )
    assert len(selected_connections_12) == 1
    assert len(selected_connections_3e) == 1
    assert (
        selected_connections_12[0].to_port is selected_connections_3e[0].to_port
    )  # output3 is same

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(
        join(
            abspath(dirname(__file__)), "components_model1", "example_inherit2.components"
        )
    )

    #################################
    # TEST MODEL
    #################################

    # test inherited ports are same
    # (indirect inheritance: Middle -> Start -> End)
    action1 = get_unique_named_object(my_model, "action1")
    action2 = get_unique_named_object(my_model, "action2")
    action3 = get_unique_named_object(my_model, "action3")
    end = get_unique_named_object(my_model, "end")
    connections = get_children_of_type("Connection", my_model)
    selected_connections_12 = list(
        filter(lambda x: x.from_inst == action1 and x.to_inst == action2, connections)
    )
    selected_connections_3e = list(
        filter(lambda x: x.from_inst == action3 and x.to_inst == end, connections)
    )
    assert len(selected_connections_12) == 1
    assert len(selected_connections_3e) == 1
    assert (
        selected_connections_12[0].to_port is selected_connections_3e[0].to_port
    )  # output3 is same

    #################################
    # END
    #################################


def test_model_with_local_scope_postponed():
    """
    This is a test for the local scope provider which checks that
    the scope resolution is postponed at an intermediate stage.

    This must be the case, since the order of object references is
    exchanged in two differernt metamodels. This, we argue that (in the
    absence of an additional sorting mechanisms) in one of both
    cases the required reference to the "from_instance" must be unresolved
    in the first resolution pass.

    The check is done using white box information (postponed_counter).
    """
    #################################
    # META MODEL DEF
    #################################

    sp1 = scoping_providers.RelativeName("from_inst.component.slots")
    my_meta_model1 = metamodel_from_file(
        join(abspath(dirname(__file__)), "components_model1", "Components.tx")
    )
    my_meta_model1.register_scope_providers(
        {
            "*.*": scoping_providers.FQN(),
            "Connection.from_port": sp1,
            "Connection.to_port": scoping_providers.RelativeName(
                "to_inst.component.slots"
            ),
        }
    )

    sp2 = scoping_providers.RelativeName("from_inst.component.slots")
    my_meta_model2 = metamodel_from_file(
        join(abspath(dirname(__file__)), "components_model2", "Components.tx")
    )
    my_meta_model2.register_scope_providers(
        {
            "*.*": scoping_providers.FQN(),
            "Connection.from_port": sp2,
            "Connection.to_port": scoping_providers.RelativeName(
                "to_inst.component.slots"
            ),
        }
    )

    #################################
    # MODEL PARSING
    #################################

    my_meta_model1.model_from_file(
        join(abspath(dirname(__file__)), "components_model1", "example.components")
    )
    my_meta_model2.model_from_file(
        join(abspath(dirname(__file__)), "components_model2", "example.components")
    )

    #################################
    # TEST MODEL
    #################################

    assert sp1.postponed_counter > 0 or sp2.postponed_counter > 0

    #################################
    # END
    #################################


def test_model_with_local_scope_wrong_type():
    """
    This is a basic test for the local scope provider
    (basd case with wrong type).
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "components_model1", "Components.tx")
    )
    my_meta_model.register_scope_providers(
        {
            "*.*": scoping_providers.FQN(),
            "Connection.from_port": scoping_providers.RelativeName(
                "from_inst.component.slots"
            ),
            "Connection.to_port": scoping_providers.RelativeName(
                "to_inst.component.slots"
            ),
        }
    )

    #################################
    # MODEL PARSING
    #################################

    with raises(textx.exceptions.TextXSemanticError, match=r".*wrong_port.*"):
        my_meta_model.model_from_file(
            join(
                abspath(dirname(__file__)),
                "components_model1",
                "example_wrong_type.components",
            )
        )


def test_model_with_local_scope_and_bad_model_path():
    """
    This is a basic test for the local scope provider
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "components_model1", "Components.tx")
    )
    my_meta_model.register_scope_providers(
        {
            "*.*": scoping_providers.FQN(),
            "Connection.from_port":
            # error (component is not a list)
            scoping_providers.RelativeName("from_inst.component"),
            "Connection.to_port": scoping_providers.RelativeName(
                "to_inst.component.slots"
            ),
        }
    )

    #################################
    # MODEL PARSING
    #################################

    with raises(
        textx.exceptions.TextXError,
        match=r".*expected path to list in the model " + r"\(from_inst.component\).*",
    ):
        my_meta_model.model_from_file(
            join(abspath(dirname(__file__)), "components_model1", "example.components")
        )
