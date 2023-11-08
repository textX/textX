from os.path import abspath, dirname, join

from pytest import raises

import textx.scoping.providers as scoping_providers
from textx import metamodel_from_file
from textx.scoping.tools import (
    check_unique_named_object_has_class,
    get_unique_named_object,
)


def test_globalimports_basic_test_with_single_model_file():
    """
    Basic test for the FQNGlobalRepo.
    Tests that two metamodels create different objects for the
    same input.
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "interface_model2", "Interface.tx")
    )
    my_meta_model.register_scope_providers(
        {
            "*.*": scoping_providers.FQNGlobalRepo(
                join(abspath(dirname(__file__)), "interface_model2", "model_a", "*.if")
            )
        }
    )

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(
        join(abspath(dirname(__file__)), "interface_model2", "model_a", "all_in_one.if")
    )
    my_model2 = my_meta_model.model_from_file(
        join(abspath(dirname(__file__)), "interface_model2", "model_a", "all_in_one.if")
    )

    #################################
    # TEST MODEL
    #################################

    # check that "socket" is an interface
    check_unique_named_object_has_class(my_model, "socket", "Interface")

    # check that "s.s1" is a reference to the socket interface
    a = get_unique_named_object(my_model, "socket")
    s1 = get_unique_named_object(my_model, "s1")
    assert a == s1.ref

    a2 = get_unique_named_object(my_model2, "socket")
    assert a2 != a  # no global repository

    #################################
    # END
    #################################


def test_globalimports_basic_test_with_single_model_file_and_global_repo():
    """
    Basic test for the FQNGlobalRepo + global_repository.
    Tests that two metamodels create the same objects for the
    same input (when global_repository is used).
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "interface_model2", "Interface.tx"),
        global_repository=True,
    )
    my_meta_model.register_scope_providers(
        {
            "*.*": scoping_providers.FQNGlobalRepo(
                join(abspath(dirname(__file__)), "interface_model2", "model_a", "*.if")
            )
        }
    )

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(
        join(abspath(dirname(__file__)), "interface_model2", "model_a", "all_in_one.if")
    )
    my_model2 = my_meta_model.model_from_file(
        join(abspath(dirname(__file__)), "interface_model2", "model_a", "all_in_one.if")
    )

    #################################
    # TEST MODEL
    #################################

    # check that "socket" is an interface
    check_unique_named_object_has_class(my_model, "socket", "Interface")

    # check that "s.s1" is a reference to the socket interface
    a = get_unique_named_object(my_model, "socket")
    s1 = get_unique_named_object(my_model, "s1")
    assert a == s1.ref

    a2 = get_unique_named_object(my_model2, "socket")
    assert a2 == a  # with global repository

    #################################
    # END
    #################################


def test_globalimports_basic_test_with_distributed_model():
    """
    Basic test for the FQNGlobalRepo.
    Tests that a reference points to the expected (python) object
    located in the model.
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "interface_model2", "Interface.tx")
    )
    my_meta_model.register_scope_providers(
        {
            "*.*": scoping_providers.FQNGlobalRepo(
                join(abspath(dirname(__file__)), "interface_model2", "model_b", "*.if")
            )
        }
    )

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(
        join(abspath(dirname(__file__)), "interface_model2", "model_b", "app.if")
    )

    #################################
    # TEST MODEL
    #################################

    # check that "socket" is an interface
    inner_model = my_model._tx_model_repository.all_models[
        join(abspath(dirname(__file__)), "interface_model2", "model_b", "base.if")
    ]
    check_unique_named_object_has_class(inner_model, "socket", "Interface")

    # check that "s.s1" is a reference to the socket interface
    a = get_unique_named_object(inner_model, "socket")
    s1 = get_unique_named_object(inner_model, "s1")
    assert a == s1.ref

    #################################
    # END
    #################################


def test_globalimports_with_project_root_model_parameter():
    """
    Basic test for the FQNGlobalRepo.
    Tests that "project_root" model parameter has an effect.
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "interface_model2", "Interface.tx")
    )
    my_meta_model.register_scope_providers(
        {"*.*": scoping_providers.FQNGlobalRepo(join("model_a", "*.if"))}
    )

    #################################
    # MODEL PARSING
    #################################

    with raises(IOError):
        _ = my_meta_model.model_from_file(
            join(
                abspath(dirname(__file__)), "interface_model2", "model_a", "all_in_one.if"
            )
        )

    _ = my_meta_model.model_from_file(
        join(abspath(dirname(__file__)), "interface_model2", "model_a", "all_in_one.if"),
        project_root=join(abspath(dirname(__file__)), "interface_model2"),
    )

    #################################
    # END
    #################################
