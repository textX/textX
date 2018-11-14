from __future__ import unicode_literals

from textx import metamodel_from_str
from os.path import dirname, abspath
import textx.exceptions
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
        
        Var: 'var' name=ID '=' 'new' class=[Class|FQN] '(' ')';
        
        FQN: ID+['.'];
        Import: 'import' importURI=STRING;
        Comment: /#.*$/;
        ''')

    def name_setter(import_obj):
        import re
        m = re.search(r'^([^\.]+).*$', import_obj.importURI)
        assert m
        return m.group(1)

    mm.register_scope_providers(
        {"*.*": scoping_providers.FQNImportURI(importAs=True, name_setter=name_setter)})

    #################################
    # MODEL PARSING
    #################################

    m = mm.model_from_file(
        abspath(dirname(__file__)) + "/issue103/main.mod")

    #################################
    # TEST MODEL
    #################################

    #assert my_model.packages[0].name == "B"

    #################################
    # END
    #################################
