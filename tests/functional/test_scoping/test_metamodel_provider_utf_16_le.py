from os.path import abspath, dirname, join

import textx.scoping.providers as scoping_providers
from textx import clear_language_registrations, metamodel_from_file, register_language
from textx.scoping.tools import get_unique_named_object_in_all_models


def test_metamodel_provider_utf_16_le_basic_test():
    """
    This test checks that the global MetaModel Provider
    works (basic function). It uses utf-16-le for the model files.
    """
    #################################
    # META MODEL DEF
    #################################

    mm_components = metamodel_from_file(
        join(abspath(dirname(__file__)), "metamodel_provider_utf-16-le", "Components.tx")
    )
    mm_components.register_scope_providers(
        {
            "*.*": scoping_providers.FQNImportURI(),
            "Connection.from_port": scoping_providers.RelativeName(
                "from_inst.component.slots"
            ),
            "Connection.to_port": scoping_providers.RelativeName(
                "to_inst.component.slots"
            ),
        }
    )

    mm_users = metamodel_from_file(
        join(abspath(dirname(__file__)), "metamodel_provider_utf-16-le", "Users.tx")
    )
    mm_users.register_scope_providers(
        {
            "*.*": scoping_providers.FQNImportURI(),
        }
    )

    clear_language_registrations()
    register_language(
        "components-dsl",
        pattern="*.components",
        description="demo",
        metamodel=mm_components,  # or a factory
    )
    register_language(
        "users-dsl",
        pattern="*.users",
        description="demo",
        metamodel=mm_users,  # or a factory
    )

    #################################
    # MODEL PARSING
    #################################

    my_model = mm_users.model_from_file(
        join(abspath(dirname(__file__)), "metamodel_provider_utf-16-le", "example.users"),
        encoding="utf-16-le",
    )

    #################################
    # TEST MODEL
    #################################

    user = get_unique_named_object_in_all_models(my_model, "pi")
    action1 = get_unique_named_object_in_all_models(my_model, "action1")

    assert user.instance is action1

    #################################
    # END
    #################################
