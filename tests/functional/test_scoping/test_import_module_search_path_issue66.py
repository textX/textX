from __future__ import unicode_literals

from os.path import dirname, abspath
import textx.scoping.providers as scoping_providers
from textx import metamodel_from_file
from pytest import raises


def test_model_with_imports_and_search_path_bad_case1():
    """
    Basic test for ImportURI (bad case: no search path)
    """
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        abspath(dirname(__file__)) + '/issue66/task_specification.tx')
    my_meta_model.register_scope_providers(
        {"*.*": scoping_providers.PlainNameImportURI()})

    #################################
    # MODEL PARSING
    #################################

    with raises(FileNotFoundError, match=r'.*lib.*tasks.*'):
        _ = my_meta_model.model_from_file(
            abspath(dirname(__file__)) + "/issue66/assembly_car1.prog")

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
        abspath(dirname(__file__)) + '/issue66/task_specification.tx')
    search_path = [
        abspath(dirname(__file__)) + '/issue66/somewhere1',
        abspath(dirname(__file__)) + '/issue66/somewhere2'
    ]
    my_meta_model.register_scope_providers(
        {"*.*": scoping_providers.PlainNameImportURI(search_path=search_path)})

    #################################
    # MODEL PARSING
    #################################

    _ = my_meta_model.model_from_file(
        abspath(dirname(__file__)) + "/issue66/assembly_car1.prog")

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
        abspath(dirname(__file__)) + '/issue66/task_specification.tx')
    search_path = [
        abspath(dirname(__file__)) + '/issue66/somewhere1',  # assembly
        abspath(dirname(__file__)) + '/issue66/somewhere2xx'  # position
    ]
    my_meta_model.register_scope_providers(
        {"*.*": scoping_providers.PlainNameImportURI(search_path=search_path)})

    #################################
    # MODEL PARSING
    #################################

    with raises(FileNotFoundError, match=r'.*position\.tasks.*'):
        _ = my_meta_model.model_from_file(
            abspath(dirname(__file__)) + "/issue66/assembly_car1.prog")

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
        abspath(dirname(__file__)) + '/issue66/task_specification.tx')
    search_path = [
        abspath(dirname(__file__)) + '/issue66/somewhere1xx',  # assembly
        abspath(dirname(__file__)) + '/issue66/somewhere2'  # position
    ]
    my_meta_model.register_scope_providers(
        {"*.*": scoping_providers.PlainNameImportURI(search_path=search_path)})

    #################################
    # MODEL PARSING
    #################################

    with raises(FileNotFoundError, match=r'.*assembly\.tasks.*'):
        _ = my_meta_model.model_from_file(
            abspath(dirname(__file__)) + "/issue66/assembly_car1.prog")

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
        abspath(dirname(__file__)) + '/issue66/task_specification.tx')
    search_path = [
        abspath(dirname(__file__)) + '/issue66/somewhere1',  # assembly
        abspath(dirname(__file__)) + '/issue66/somewhere2'  # position
    ]
    with raises(Exception,
                match=r'you cannot use globbing together with a search path'):
        my_meta_model.register_scope_providers(
            {"*.*": scoping_providers.PlainNameImportURI(glob_args={},
                                                         search_path=search_path)})

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
        abspath(dirname(__file__)) + '/issue66/task_specification.tx')
    search_path = [
        abspath(dirname(__file__)) + '/issue66/somewhere1',  # assembly
        abspath(dirname(__file__)) + '/issue66/somewhere2'   # position
    ]
    my_meta_model.register_scope_providers(
        {"*.*": scoping_providers.PlainNameImportURI(search_path=search_path)})

    #################################
    # MODEL PARSING
    #################################

    with raises(FileNotFoundError, match=r'.*assembly\.\*.*'):
        _ = my_meta_model.model_from_file(
            abspath(dirname(__file__)) + "/issue66/assembly_car2.prog")

    #################################
    # END
    #################################