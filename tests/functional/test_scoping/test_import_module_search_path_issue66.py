from os.path import abspath, dirname, join

from pytest import raises

import textx.scoping.providers as scoping_providers
from textx import metamodel_from_file


def test_model_with_imports_and_search_path_bad_case1():
    """
    Basic test for ImportURI (bad case: no search path)
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "issue66", "task_specification.tx")
    )
    my_meta_model.register_scope_providers(
        {"*.*": scoping_providers.PlainNameImportURI()}
    )

    #################################
    # MODEL PARSING
    #################################

    with raises(IOError, match=r".*lib.*tasks.*"):
        my_meta_model.model_from_file(
            join(abspath(dirname(__file__)), "issue66", "assembly_car1.prog")
        )

    #################################
    # END
    #################################


def test_model_with_imports_and_search_path_good_case():
    """
    Basic test for ImportURI (good case)
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "issue66", "task_specification.tx")
    )
    search_path = [
        join(abspath(dirname(__file__)), "issue66", "somewhere1"),
        join(abspath(dirname(__file__)), "issue66", "somewhere2"),
    ]
    my_meta_model.register_scope_providers(
        {"*.*": scoping_providers.PlainNameImportURI(search_path=search_path)}
    )

    #################################
    # MODEL PARSING
    #################################

    my_meta_model.model_from_file(
        join(abspath(dirname(__file__)), "issue66", "assembly_car1.prog")
    )

    #################################
    # END
    #################################


def test_model_with_imports_and_search_path_bad_case2a():
    """
    Basic test for ImportURI (bad case)
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "issue66", "task_specification.tx")
    )
    search_path = [
        join(abspath(dirname(__file__)), "issue66", "somewhere1"),  # assembly
        join(abspath(dirname(__file__)), "issue66", "somewhere2xx"),  # position
    ]
    my_meta_model.register_scope_providers(
        {"*.*": scoping_providers.PlainNameImportURI(search_path=search_path)}
    )

    #################################
    # MODEL PARSING
    #################################

    with raises(IOError, match=r".*position\.tasks.*"):
        my_meta_model.model_from_file(
            join(abspath(dirname(__file__)), "issue66", "assembly_car1.prog")
        )

    #################################
    # END
    #################################


def test_model_with_imports_and_search_path_bad_case2b():
    """
    Basic test for ImportURI (bad case)
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "issue66", "task_specification.tx")
    )
    search_path = [
        join(abspath(dirname(__file__)), "issue66", "somewhere1xx"),  # assembly
        join(abspath(dirname(__file__)), "issue66", "somewhere2"),  # position
    ]
    my_meta_model.register_scope_providers(
        {"*.*": scoping_providers.PlainNameImportURI(search_path=search_path)}
    )

    #################################
    # MODEL PARSING
    #################################

    with raises(IOError, match=r".*assembly\.tasks.*"):
        my_meta_model.model_from_file(
            join(abspath(dirname(__file__)), "issue66", "assembly_car1.prog")
        )

    #################################
    # END
    #################################


def test_model_with_imports_and_search_path_bad_case_search_and_glob1():
    """
    Basic test for ImportURI (bad case: search_path + globbing)
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
    with raises(Exception, match=r"you cannot use globbing together with a search path"):
        my_meta_model.register_scope_providers(
            {
                "*.*": scoping_providers.PlainNameImportURI(
                    glob_args={}, search_path=search_path
                )
            }
        )

    #################################
    # END
    #################################


def test_model_with_imports_and_search_path_bad_case_search_and_glob2():
    """
    Basic test for ImportURI (bad case: with search path no file patterns are
    allowed)
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

    with raises(IOError, match=r".*assembly\.\*.*"):
        my_meta_model.model_from_file(
            join(abspath(dirname(__file__)), "issue66", "assembly_car2.prog")
        )

    #################################
    # END
    #################################


def test_model_with_imports_relative_to_current_model():
    """
    Basic test for ImportURI (good case: it should always be preferred
    to load relative to the current model file)
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
    # * on only exists locally.
    m = my_meta_model.model_from_file(
        join(abspath(dirname(__file__)), "issue66", "local", "assembly_car3.prog")
    )

    # the model could be loaded --> the local path works (one file exists
    # only locally).

    assert len(m.imports) == 2
    dirs = list(map(lambda i: dirname(i._tx_loaded_models[0]._tx_filename), m.imports))
    assert dirs[0] == dirs[1]
    # both included model have the same location. Thus, the local path is
    # preferred (as designed through the order of search paths).

    #################################
    # END
    #################################
