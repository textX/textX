from __future__ import unicode_literals

from textx import metamodel_from_str
from os.path import dirname, abspath
from pytest import raises
import textx.exceptions
import textx.scoping.providers as scoping_providers


def test_importURI_variations_import_string_hook():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_str('''
Model:
        imports*=Import
        packages*=Package
;

Package:
        'package' name=ID '{'
            objects*=Object
        '}'
;

Object:
    'object' name=ID text=STRING ('ref' ref=[Object|FQN])? ';'?
;

FQN: ID+['.'];
Import: 'import' importURI=FQN;
Comment: /\/\/.*$/;
    ''')

    def conv(i):
        return i.replace(".", "/")+".model"

    my_meta_model.register_scope_providers(
        {"*.*": scoping_providers.FQNImportURI(importURI_converter=conv)})

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(
        abspath(dirname(__file__)) + "/importStringHook/b.model")

    #################################
    # TEST MODEL
    #################################

    assert my_model.packages[0].name == "B"
    assert my_model.packages[0].objects[0].name == "A1"
    assert my_model.packages[0].objects[0].ref.text == "from A1"
    assert my_model.packages[0].objects[1].name == "A2"
    assert my_model.packages[0].objects[1].ref.text == "from A2"

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
