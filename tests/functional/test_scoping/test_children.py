import re
from operator import eq

import textx.scoping.providers as scoping_providers
from textx import get_children, get_children_of_type, metamodel_from_str

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

FQN: ID('.'ID)*;
    """


def test_children():
    """
    This test checks the get_children function
    """
    #################################
    # META MODEL DEF
    #################################

    my_metamodel = metamodel_from_str(metamodel_str)

    my_metamodel.register_scope_providers({"*.*": scoping_providers.FQN()})

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
    # TEST
    #################################

    res = get_children_of_type("Class", my_model)
    res.sort(key=lambda x: x.name)
    assert len(res) == 3
    assert all(map(eq, map(lambda x: x.name, res), ["C2", "Part1", "Part2"]))
    assert not all(map(eq, map(lambda x: x.name, res), ["Part1", "Part2", "C2"]))
    for x in res:
        assert x.__class__.__name__ == "Class"

    res = get_children_of_type("Attribute", my_model)
    res.sort(key=lambda x: x.name)
    assert len(res) == 4
    assert all(map(eq, map(lambda x: x.name, res), ["p1", "p2a", "p2b", "rec"]))
    for x in res:
        assert x.__class__.__name__ == "Attribute"

    res = get_children(
        lambda x: hasattr(x, "name") and re.match(".*2.*", x.name), my_model
    )
    res.sort(key=lambda x: x.name)
    assert len(res) == 5
    assert all(map(eq, map(lambda x: x.name, res), ["C2", "P2", "Part2", "p2a", "p2b"]))

    #################################
    # END
    #################################
