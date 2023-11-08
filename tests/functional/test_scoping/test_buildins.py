from pytest import raises

import textx.exceptions
import textx.scoping.providers as scoping_providers
from textx import metamodel_from_str

metamodel_str = """
Model:
    persons*=Person
    things+=Thing
    refs*=PersonRef
;
Person: 'person' name=ID;
PersonRef: 'ref' ref=[Person];
Thing:
    'thing' name=ID '{'
    inner*=[Thing]
    '}'
;

"""


class Thing:
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])


def test_buildins():
    """
    This test is used to check if a model with buildins works correctly.
    The test uses no special scoping.

    The test loads
    - one model w/o buildins
    - one model with buildins
    - one model with unknown references (errors)
    - one model with references to builtins of wrong type
    """
    #################################
    # META MODEL DEF
    #################################

    type_builtins = {
        "OneThing": Thing(name="OneThing"),
        "OtherThing": Thing(name="OtherThing"),
    }
    my_metamodel = metamodel_from_str(
        metamodel_str, classes=[Thing], builtins=type_builtins
    )

    #################################
    # MODEL PARSING
    #################################

    my_metamodel.model_from_str(
        """
    person P
    person I
    thing A {}
    thing B {}
    thing C {A B}
    ref P
    ref I
    """
    )

    my_metamodel.model_from_str(
        """
    person P
    person I
    thing A {}
    thing B {}
    thing C {A B OneThing OtherThing}
    ref P
    ref I
    """
    )

    with raises(
        textx.exceptions.TextXSemanticError, match=r".*Unknown object.*UnknownPart.*"
    ):
        my_metamodel.model_from_str(
            """
        thing A {}
        thing B {}
        thing C {A B OneThing OtherThing UnknownPart}
        """
        )

    with raises(
        textx.exceptions.TextXSemanticError,
        match=r'.*Unknown object "OneThing" of class "Person".*',
    ):
        my_metamodel.model_from_str(
            """
            person P
            person I
            thing A {}
            thing B {}
            thing C {A B OneThing OtherThing}
            ref OneThing
            ref OtherThing
        """
        )

    #################################
    # END
    #################################


def test_buildins_fully_qualified_name():
    """
    This test is used to check if a model with buildins works correctly.
    The test uses full quialified name scoping (to check that exchanging the
    scope provider globally does not harm the buildins-feature.

    The test loads
    - one model w/o buildins
    - one model with buildins
    - one model with unknown references (errors)
    - one model with references to builtins of wrong type
    """
    #################################
    # META MODEL DEF
    #################################

    type_builtins = {
        "OneThing": Thing(name="OneThing"),
        "OtherThing": Thing(name="OtherThing"),
    }
    my_metamodel = metamodel_from_str(
        metamodel_str, classes=[Thing], builtins=type_builtins
    )
    my_metamodel.register_scope_providers({"*.*": scoping_providers.FQN()})

    #################################
    # MODEL PARSING
    #################################

    my_metamodel.model_from_str(
        """
    person P
    person I
    thing A {}
    thing B {}
    thing C {A B}
    ref P
    ref I
    """
    )

    my_metamodel.model_from_str(
        """
    person P
    person I
    thing A {}
    thing B {}
    thing C {A B OneThing OtherThing}
    ref P
    ref I
    """
    )

    with raises(
        textx.exceptions.TextXSemanticError, match=r".*Unknown object.*UnknownPart.*"
    ):
        my_metamodel.model_from_str(
            """
        thing A {}
        thing B {}
        thing C {A B OneThing OtherThing UnknownPart}
        """
        )

    with raises(
        textx.exceptions.TextXSemanticError,
        match=r'.*Unknown object "OneThing" of class "Person".*',
    ):
        my_metamodel.model_from_str(
            """
            person P
            person I
            thing A {}
            thing B {}
            thing C {A B OneThing OtherThing}
            ref OneThing
            ref OtherThing
        """
        )

    #################################
    # END
    #################################
