from os.path import abspath, dirname, join

import textx.scoping.providers as scoping_providers
from textx import metamodel_from_file
from textx.scoping import is_file_included


def test_inclusion_check_1():
    """
    Test to demonstrate how to check if a file is used by a model.
    This can be used by an IDE to determine, if a model has to be
    updated/reloaded.
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "issue66", "task_specification.tx")
    )
    search_path = [
        join(abspath(dirname(__file__)), "issue66", "somewhere1"),  # assembly
        join(abspath(dirname(__file__)), "issue66", "somewhere2"),  # position
    ]
    my_meta_model.register_scope_providers(
        {"*.*": scoping_providers.PlainNameImportURI(search_path=search_path)}
    )

    #################################
    # MODEL PARSING
    #################################

    # This model load two files
    # * one file exists locally and in a search path --> the local one should
    #   be preferred.
    # * one only exists locally.
    m = my_meta_model.model_from_file(
        join(abspath(dirname(__file__)), "issue66", "assembly_car1.prog")
    )

    # the model file itself is "included" (special case)
    assert is_file_included(
        join(abspath(dirname(__file__)), "issue66", "assembly_car1.prog"), m
    )
    # another model file
    assert not is_file_included(
        join(abspath(dirname(__file__)), "issue66", "local", "assembly_car3.prog"), m
    )
    # file in folder "local"
    assert not is_file_included(
        join(abspath(dirname(__file__)), "issue66", "local", "mylib", "local.tasks"), m
    )
    # file in folder "local"
    assert not is_file_included(
        join(abspath(dirname(__file__)), "issue66", "local", "mylib", "position.tasks"), m
    )
    # distant file (part of search path)
    assert is_file_included(
        join(
            abspath(dirname(__file__)), "issue66", "somewhere1", "mylib", "assembly.tasks"
        ),
        m,
    )
    # distant file (part of search path)
    assert is_file_included(
        join(
            abspath(dirname(__file__)), "issue66", "somewhere2", "mylib", "position.tasks"
        ),
        m,
    )

    #################################
    # END
    #################################


def test_inclusion_check_2():
    """
    Test to demonstrate how to check if a file is used by a model.
    This can be used by an IDE to determine, if a model has to be
    updated/reloaded.
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "issue66", "task_specification.tx")
    )
    search_path = [
        join(abspath(dirname(__file__)), "issue66", "somewhere1"),  # assembly
        join(abspath(dirname(__file__)), "issue66", "somewhere2"),  # position
    ]
    my_meta_model.register_scope_providers(
        {"*.*": scoping_providers.PlainNameImportURI(search_path=search_path)}
    )

    #################################
    # MODEL PARSING
    #################################

    # This model load two files
    # * one file exists locally and in a search path --> the local one should
    #   be preferred.
    # * one only exists locally.
    m = my_meta_model.model_from_file(
        join(abspath(dirname(__file__)), "issue66", "local", "assembly_car3.prog")
    )

    # the model file itself is "included" (special case)
    assert is_file_included(
        join(abspath(dirname(__file__)), "issue66", "local", "assembly_car3.prog"), m
    )
    # local file
    assert is_file_included(
        join(abspath(dirname(__file__)), "issue66", "local", "mylib", "local.tasks"), m
    )
    # local file
    assert is_file_included(
        join(abspath(dirname(__file__)), "issue66", "local", "mylib", "position.tasks"), m
    )
    # distant file
    assert not is_file_included(
        join(
            abspath(dirname(__file__)), "issue66", "somewhere1", "mylib", "assembly.tasks"
        ),
        m,
    )
    # distant file
    assert not is_file_included(
        join(
            abspath(dirname(__file__)), "issue66", "somewhere2", "mylib", "position.tasks"
        ),
        m,
    )

    #################################
    # END
    #################################


def test_no_tx_model_repos():
    from textx import metamodel_from_str

    mm = metamodel_from_str("Model: 'A';")
    m = mm.model_from_str("A")

    assert not is_file_included(
        join(abspath(dirname(__file__)), "issue66", "local", "mylib", "position.tasks"), m
    )
