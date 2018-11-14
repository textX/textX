from __future__ import unicode_literals

from textx import metamodel_from_str
from os.path import dirname, abspath
import textx.scoping.providers as scoping_providers


def test_issue103_python_like_import():
    """
    see issue 103 for a detailed error report
    """

    mm = metamodel_from_str(r'''
        Model:
                imports*=Import
                classes*=Class
                vars*=Var
        ;
        Class: 'class' name=ID '{' '}' ';';
        Var: 'var' name=ID '=' 'new' theclass=[Class|FQN] '(' ')';
        FQN: ID+['.'];
        Import: 'import' importURI=STRING;
        Comment: /#.*$/;
        ''')

    def importURI_to_scope_name(import_obj):
        # this method is responsible to deduce the module name in the
        # language from the importURI string
        # e.g. here: import "file.ext" --> module name "file".
        return import_obj.importURI.split('.')[0]

    mm.register_scope_providers(
        {"*.*": scoping_providers.
            FQNImportURI(importAs=True,
                         importURI_to_scope_name=importURI_to_scope_name)})

    #################################
    # MODEL PARSING
    #################################

    m = mm.model_from_file(
        abspath(dirname(__file__)) + "/issue103/main.mod")

    #################################
    # TEST MODEL
    #################################

    assert m.vars[0].theclass.name == "a"

    #################################
    # END
    #################################
