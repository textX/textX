from __future__ import unicode_literals
from textx import metamodel_from_file
from textx import get_children
import textx.scoping.providers as scoping_providers
from os.path import dirname, abspath
import textx.exceptions
from pytest import raises
from textx.scoping.tools import check_unique_named_object_has_class, \
    get_unique_named_object


def test_model_without_imports():
    """
    Basic test for FQNImportURI (with a model not using imports)
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        abspath(dirname(__file__)) + '/interface_model1/Interface.tx')
    my_meta_model.register_scope_providers(
        {"*.*": scoping_providers.FQNImportURI()})

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(
        abspath(dirname(__file__)) + "/interface_model1/model_a/all_in_one.if")

    #################################
    # TEST MODEL
    #################################

    # check that "socket" is an interface
    check_unique_named_object_has_class(my_model, "socket", "Interface")

    # check that "s.s1" is a reference to the socket interface
    a = get_unique_named_object(my_model, "socket")
    s1 = get_unique_named_object(my_model, "s1")
    assert a == s1.ref

    #################################
    # END
    #################################


def test_model_with_imports():
    """
    Basic test for FQNImportURI (good case)
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        abspath(dirname(__file__)) + '/interface_model1/Interface.tx')
    my_meta_model.register_scope_providers(
        {"*.*": scoping_providers.FQNImportURI()})

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(
        abspath(dirname(__file__)) + "/interface_model1/model_b/app.if")
    my_model2 = my_meta_model.model_from_file(
        abspath(dirname(__file__)) + "/interface_model1/model_b/app.if")

    #################################
    # TEST MODEL
    #################################

    # check that "socket" is an interface
    inner_model = my_model._tx_model_repository.all_models.filename_to_model[
        abspath(dirname(__file__)) + "/interface_model1/model_b/base.if"]
    check_unique_named_object_has_class(inner_model, "socket", "Interface")

    # check that "s.s1" is a reference to the socket interface
    a = get_unique_named_object(inner_model, "socket")
    s1 = get_unique_named_object(inner_model, "s1")
    userid = get_unique_named_object(my_model, "userid")
    assert a == s1.ref

    userid2 = get_unique_named_object(my_model2, "userid")
    assert userid != userid2
    assert userid.ref != userid2.ref
    assert userid.ref.__class__.__name__ == "RawType"

    #################################
    # END
    #################################


def test_model_with_imports_and_errors():
    """
    Basic test for FQNImportURI (bad case)
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        abspath(dirname(__file__)) + '/interface_model1/Interface.tx')
    my_meta_model.register_scope_providers(
        {"*.*": scoping_providers.FQNImportURI()})

    #################################
    # MODEL PARSING
    #################################

    with raises(textx.exceptions.TextXSemanticError,
                match=r'.*Unknown object.*types.int.*'):
        _ = my_meta_model.model_from_file(
            abspath(dirname(__file__)) +
            "/interface_model1/model_b/app_error1.if")

    with raises(IOError, match=r'.*file_not_found\.if.*'):
        _ = my_meta_model.model_from_file(
            abspath(dirname(__file__)) +
            "/interface_model1/model_b/app_error2.if")

    #################################
    # END
    #################################


def test_model_with_imports_and_global_repo():
    """
    Basic test for FQNImportURI + global_repository
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        abspath(dirname(__file__)) + '/interface_model1/Interface.tx',
        global_repository=True)
    my_meta_model.register_scope_providers(
        {"*.*": scoping_providers.FQNImportURI()})

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(
        abspath(dirname(__file__)) + "/interface_model1/model_b/app.if")
    my_model2 = my_meta_model.model_from_file(
        abspath(dirname(__file__)) + "/interface_model1/model_b/app.if")

    #################################
    # TEST MODEL
    #################################

    userid = get_unique_named_object(my_model, "userid")
    userid2 = get_unique_named_object(my_model2, "userid")
    assert userid == userid2
    assert userid.ref == userid2.ref
    assert userid.ref.__class__.__name__ == "RawType"

    #################################
    # END
    #################################


def test_model_with_circular_imports():
    """
    Basic test for FQNImportURI + circular imports
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        abspath(dirname(__file__)) + '/interface_model1/Interface.tx')
    my_meta_model.register_scope_providers(
        {"*.*": scoping_providers.FQNImportURI()})

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(
        abspath(dirname(__file__)) + "/interface_model1/model_c/A.if")

    #################################
    # TEST MODEL
    #################################

    check_unique_named_object_has_class(my_model, "A", "Interface")
    a = get_unique_named_object(my_model, "A")

    a_self = get_children(lambda x: hasattr(x, 'name') and x.name == "self", a)
    assert len(a_self) == 1
    a_self = a_self[0]

    a_other = get_children(
        lambda x: hasattr(x, 'name') and x.name == "other", a)
    assert len(a_other) == 1
    a_other = a_other[0]

    a_other_self = get_children(
        lambda x: hasattr(x, 'name') and x.name == "self", a_other.ref)
    assert len(a_other_self) == 1
    a_other_self = a_other_self[0]

    a_other_other = get_children(
        lambda x: hasattr(x, 'name') and x.name == "other", a_other.ref)
    assert len(a_other_other) == 1
    a_other_other = a_other_other[0]

    assert a_self.ref == a_other_other.ref
    assert a_self.ref != a_other.ref
    assert a_other.ref == a_other_self.ref
    assert a_other.ref != a_other_other.ref

    #################################
    # END
    #################################
