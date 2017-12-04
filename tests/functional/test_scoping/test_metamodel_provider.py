from __future__ import unicode_literals
from textx import metamodel_from_file
import textx.scoping.providers as scoping_providers
import textx.scoping as scoping
from os.path import dirname, abspath
from textx.scoping.tools import get_unique_named_object_in_all_models
from pytest import raises


def test_metamodel_provder_basic_test():
    #################################
    # META MODEL DEF
    #################################

    mm_components = metamodel_from_file(
        abspath(dirname(__file__)) + '/metamodel_provider/Components.tx')
    mm_components.register_scope_providers({
        "*.*": scoping_providers.FQNImportURI(),
        "Connection.from_port":
            scoping_providers.RelativeName("from_inst.component.slots"),
        "Connection.to_port":
            scoping_providers.RelativeName("to_inst.component.slots"),
    })

    mm_users = metamodel_from_file(
        abspath(dirname(__file__)) + '/metamodel_provider/Users.tx')
    mm_users.register_scope_providers({
        "*.*": scoping_providers.FQNImportURI(),
    })

    scoping.MetaModelProvider.add_metamodel("*.components", mm_components)
    scoping.MetaModelProvider.add_metamodel("*.users", mm_users)
    with raises(Exception, match=r'.*pattern.*already registered.*'):
        scoping.MetaModelProvider.add_metamodel("*.users", mm_users)

    #################################
    # MODEL PARSING
    #################################

    my_model = mm_users.model_from_file(
        abspath(dirname(__file__)) + "/metamodel_provider/example.users")

    #################################
    # TEST MODEL
    #################################

    user = get_unique_named_object_in_all_models(my_model, "pi")
    action1 = get_unique_named_object_in_all_models(my_model, "action1")

    assert user.instance is action1

    #################################
    # END
    #################################
