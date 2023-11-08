from os.path import dirname, join

from pytest import raises

import textx.exceptions
from textx import get_children, metamodel_from_str

metamodel_str = """
Model:
    packages*=Package
;

Package:
    'package' name=ID '{'
    classes*=Class
    '}'
;

Class:
    'class' name=ID '{'
        attributes*=Attribute
    '}'
;

Attribute:
        'attr' ref=[Class:FQN] name=ID ';'
;

Comment: /#.*/;
FQN: ID('.'ID)*;
"""


def test_fully_qualified_name_ref():
    """
    This is a basic test for the FQN (positive and negative test).
    """
    #################################
    # META MODEL DEF
    #################################

    my_metamodel = metamodel_from_str(metamodel_str)

    my_metamodel.register_scope_providers({"Attribute.ref": "^packages*.classes"})

    #################################
    # MODEL PARSING
    #################################

    my_model = my_metamodel.model_from_str(
        """
    package P1 {
        class Part1 {
        }
    }
    package P2 {
        class Part2 {
            attr C2 rec;
        }
        class C2 {
            attr P1.Part1 p1;
            attr Part2 p2a;
            attr P2.Part2 p2b;
        }
    }
    """
    )

    #################################
    # TEST MODEL
    #################################

    a = get_children(lambda x: hasattr(x, "name") and x.name == "rec", my_model)
    assert len(a) == 1
    assert a[0].name == "rec"
    assert a[0].ref.__class__.__name__ == "Class"
    assert a[0].ref.name == "C2"

    a = get_children(lambda x: hasattr(x, "name") and x.name == "p1", my_model)
    assert len(a) == 1
    assert a[0].name == "p1"
    assert a[0].ref.__class__.__name__ == "Class"
    assert a[0].ref.name == "Part1"

    a = get_children(lambda x: hasattr(x, "name") and x.name == "p2a", my_model)
    assert len(a) == 1
    assert a[0].name == "p2a"
    assert a[0].ref.__class__.__name__ == "Class"
    assert a[0].ref.name == "Part2"

    a = get_children(lambda x: hasattr(x, "name") and x.name == "p2b", my_model)
    assert len(a) == 1
    assert a[0].name == "p2b"
    assert a[0].ref.__class__.__name__ == "Class"
    assert a[0].ref.name == "Part2"

    ###########################
    # MODEL WITH ERROR
    ############################
    with raises(
        textx.exceptions.TextXSemanticError, match=r"None:8:.*: Unknown object.*Part1.*"
    ):
        my_metamodel.model_from_str(
            """ #1
        package P1 { #2
            class Part1 { #3
            } #4
        } #5
        package P2 { #6
            class C2 { #7
                attr Part1 p1; #8
            }
        }
        """
        )

    with raises(
        textx.exceptions.TextXSemanticError,
        match=r".*test_fully_qualified_name_test_error.model:8:\d+:"
        " Unknown object.*Part1.*",
    ):
        my_metamodel.model_from_file(
            join(dirname(__file__), "misc", "test_fully_qualified_name_test_error.model")
        )

    #################################
    # END
    #################################


def test_fully_qualified_name_ref_with_splitstring():
    """
    This is a basic test for the FQN (positive and negative test).
    """
    #################################
    # META MODEL DEF
    #################################

    my_metamodel = metamodel_from_str(
        r"""
        Model: packages*=Package;
        Package: 'package' name=ID '{' classes*=Class '}';
        Class: 'class' name=ID '{'attributes*=Attribute'}';
        Attribute: 'attr' ref=[Class:FQN] name=ID ';';
        Comment: /#.*/;
        FQN[split='/']: ID('/'ID)*;
    """
    )

    my_metamodel.register_scope_providers({"Attribute.ref": "^packages*.classes"})

    #################################
    # MODEL PARSING
    #################################

    my_model = my_metamodel.model_from_str(
        """
    package P1 {
        class Part1 {
        }
    }
    package P2 {
        class Part2 {
            attr C2 rec;
        }
        class C2 {
            attr P1/Part1 p1;
            attr Part2 p2a;
            attr P2/Part2 p2b;
        }
    }
    """
    )

    #################################
    # TEST MODEL
    #################################

    a = get_children(lambda x: hasattr(x, "name") and x.name == "rec", my_model)
    assert len(a) == 1
    assert a[0].name == "rec"
    assert a[0].ref.__class__.__name__ == "Class"
    assert a[0].ref.name == "C2"


def test_split_param_without_delimiter():
    with raises(
        textx.exceptions.TextXError, match=r".*split requires a string parameter.*"
    ):
        metamodel_from_str(
            """
            FQN[split]: ID('/'ID)*;
        """
        )


def test_split_param_without_delimiter2():
    with raises(
        textx.exceptions.TextXError,
        match=r".*split requires a non-empty string parameter.*",
    ):
        metamodel_from_str(
            """
            FQN[split='']: ID('/'ID)*;
        """
        )


def test_fully_qualified_name_ref_type_error():
    """
    This is a basic test for the FQN (positive and negative test).
    """
    #################################
    # META MODEL DEF
    #################################

    my_metamodel = metamodel_from_str(metamodel_str)

    my_metamodel.register_scope_providers({"Attribute.ref": "^packages*.classes"})

    #################################
    # MODEL PARSING
    #################################

    with raises(textx.exceptions.TextXSemanticError, match=r".*p1.*"):
        my_metamodel.model_from_str(
            """
        package P1 {
            class Part1 {
            }
        }
        package P2 {
            class Part2 {
                attr C2 rec;
            }
            class C2 {
                attr P1.Part1 p1;
                attr Part2 p2a;
                attr p1 p2b;
            }
        }
        """
        )
