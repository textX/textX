from __future__ import unicode_literals

from os.path import dirname, abspath
from pytest import raises
import textx.exceptions
import textx.scoping.providers as scoping_providers


def test_importURI_variations_import_string_hook():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_str('''
        TODO
    ''')

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(
        abspath(dirname(__file__)) + "/importStringHook/b.model")

    #################################
    # TEST MODEL
    #################################

    pass
    # TODO

    #################################
    # END
    #################################

def test_importURI_variations_import_as_ok1():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_str('''
        TODO
    ''')

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(
        abspath(dirname(__file__)) + "/importAs/b_ok1.model")

    #################################
    # TEST MODEL
    #################################

    pass
    # TODO

    #################################
    # END
    #################################


def test_importURI_variations_import_as_ok2():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_str('''
        TODO
    ''')

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(
        abspath(dirname(__file__)) + "/importAs/b_ok2.model")

    #################################
    # TEST MODEL
    #################################

    pass
    # TODO

    #################################
    # END
    #################################


def test_importURI_variations_import_as_error():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_str('''
        TODO
    ''')

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(
        abspath(dirname(__file__)) + "/importAs/b_ok2.model")

    # TODO should raise error

    #################################
    # END
    #################################

