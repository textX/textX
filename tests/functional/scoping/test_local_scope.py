from textx.metamodel import metamodel_from_file
import textx.scoping as scoping
from os.path import dirname, abspath


def test_model_without_local_scope():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(abspath(dirname(__file__)) + '/components_model/Components.tx')
    my_meta_model.register_scope_provider({"*.*":scoping.scope_provider_fully_qualified_names})
    #TODO: local scope for connection

    #################################
    # MODEL PARSING
    #################################

    #TODO my_model = my_meta_model.model_from_file(abspath(dirname(__file__)) + "/components_model/example.components")

    #################################
    # TEST MODEL
    #################################

    # TODO

    #################################
    # END
    #################################
