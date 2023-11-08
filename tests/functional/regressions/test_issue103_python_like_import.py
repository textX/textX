from os.path import abspath, dirname, join

from pytest import raises

import textx.scoping.providers as scoping_providers
from textx import metamodel_from_str
from textx.exceptions import TextXSemanticError


def test_issue103_python_like_import():
    """
    see issue 103 for a detailed error report
    """

    mm = metamodel_from_str(
        r"""
        Model:
                imports*=Import
                classes*=Class
                vars*=Var
        ;
        Class: 'class' name=ID '{' '}' ';';
        Var: 'var' name=ID '=' 'new' theclass=[Class:FQN] '(' ')';
        FQN: ID+['.'];
        Import: 'import' importURI=STRING;
        Comment: /#.*$/;
        """
    )

    def importURI_to_scope_name(import_obj):
        # this method is responsible to deduce the module name in the
        # language from the importURI string
        # e.g. here: import "file.ext" --> module name "file".
        return import_obj.importURI.split(".")[0]

    mm.register_scope_providers(
        {
            "*.*": scoping_providers.FQNImportURI(
                importAs=True, importURI_to_scope_name=importURI_to_scope_name
            )
        }
    )

    #################################
    # MODEL PARSING
    #################################

    m = mm.model_from_file(join(abspath(dirname(__file__)), "issue103", "main.mod"))

    #################################
    # TEST MODEL
    #################################

    assert m.vars[0].theclass.name == "a"

    #################################
    # END
    #################################


def test_issue103_imported_namedspaces():
    """
    see issue 103 for a detailed error report
    """

    mm = metamodel_from_str(
        r"""
        Model:
                imports*=Import
                packages*=Package
                vars*=Var
        ;
        Package: PackageDef|PackageRef;
        PackageDef: "package" name=ID "{" packages*=Package classes*=Class "}";
        PackageRef: "using" ref=[Package:FQN] "as" name=ID;
        Class: 'class' name=ID '{' '}' ';';
        Var: 'var' name=ID '=' 'new' theclass=[Class:FQN] '(' ')';
        FQN: ID+['.'];
        Import: 'import' importURI=STRING;
        Comment: /#.*$/;
        """
    )

    def importURI_to_scope_name(import_obj):
        # this method is responsible to deduce the module name in the
        # language from the importURI string
        # e.g. here: import "file.ext" --> module name "file".
        return import_obj.importURI.split(".")[0]

    def custom_scope_redirection(obj):
        from textx import textx_isinstance

        if textx_isinstance(obj, mm["PackageRef"]):
            if obj.ref is None:
                from textx.scoping import Postponed

                return Postponed()
            return [obj.ref]
        else:
            return []

    mm.register_scope_providers(
        {
            "*.*": scoping_providers.FQNImportURI(
                importAs=True,
                importURI_to_scope_name=importURI_to_scope_name,
                scope_redirection_logic=custom_scope_redirection,
            )
        }
    )

    #################################
    # MODEL PARSING
    #################################

    # first test
    mm.model_from_str(
        """
        package p1 {
            package p2 {
                class a {};
            }
        }
        using p1.p2 as main
        var x = new p1.p2.a()
        var y = new main.a()
    """
    )

    # first test (negative example)
    with raises(TextXSemanticError, match=r'.*Unknown object "error.a".*'):
        mm.model_from_str(
            """
            package p1 {
                package p2 {
                    class a {};
                }
            }
            using p1.p2 as main
            var x = new p1.p2.a()
            var y = new error.a()
        """
        )

    # first test (negative example)
    with raises(TextXSemanticError, match=r'.*Unknown object "p1.error".*'):
        mm.model_from_str(
            """
            package p1 {
                package p2 {
                    class a {};
                }
            }
            using p1.error as main
            var x = new p1.p2.a()
            var y = new main.a()
        """
        )

    # second test
    m = mm.model_from_file(
        join(abspath(dirname(__file__)), "issue103", "main.packageRef")
    )

    #################################
    # TEST MODEL
    #################################

    assert m.vars[0].theclass.name == "a"

    #################################
    # END
    #################################
