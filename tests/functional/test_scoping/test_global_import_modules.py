from __future__ import unicode_literals
from textx import metamodel_from_file
import textx.scoping as scoping
from os.path import dirname, abspath
from textx.scoping_tools import get_unique_named_object, check_unique_named_object_has_class


def test_model_with_globalimports_basic_test_with_single_model_file():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(abspath(dirname(__file__)) + '/interface_model2/Interface.tx')
    my_meta_model.register_scope_providers({"*.*": scoping.ScopeProviderFullyQualifiedNamesWithGlobalRepo(
        abspath(dirname(__file__)) + "/interface_model2/model_a/*.if")})

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/interface_model2/model_a/all_in_one.if")
    my_model2 = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/interface_model2/model_a/all_in_one.if")

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


def test_model_with_globalimports_basic_test_with_single_model_file_and_with_global_repo():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(abspath(dirname(__file__)) + '/interface_model2/Interface.tx',
                                        enable_global_model_repository=True)
    my_meta_model.register_scope_providers({"*.*": scoping.ScopeProviderFullyQualifiedNamesWithGlobalRepo(
        abspath(dirname(__file__)) + "/interface_model2/model_a/*.if")})

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/interface_model2/model_a/all_in_one.if")
    my_model2 = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/interface_model2/model_a/all_in_one.if")

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
    assert a2 == a  # no global repository

    #################################
    # END
    #################################


def test_model_with_globalimports_basic_test_with_distributed_model():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(abspath(dirname(__file__)) + '/interface_model2/Interface.tx')
    my_meta_model.register_scope_providers({"*.*": scoping.ScopeProviderFullyQualifiedNamesWithGlobalRepo(
        abspath(dirname(__file__)) + "/interface_model2/model_b/*.if")})

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/interface_model2/model_b/app.if")

    #################################
    # TEST MODEL
    #################################

    # check that "socket" is an interface
    inner_model = my_model._tx_model_repository.all_models.filename_to_model[
        abspath(dirname(__file__)) + "/interface_model2/model_b/base.if"]
    check_unique_named_object_has_class(inner_model, "socket", "Interface")

    # check that "s.s1" is a reference to the socket interface
    a = get_unique_named_object(inner_model, "socket")
    s1 = get_unique_named_object(inner_model, "s1")
    assert a == s1.ref

    #################################
    # END
    #################################
