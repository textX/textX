from textx import metamodel_from_str
import textx.scoping as scoping
import textx.exceptions
from pytest import raises

metamodel_str = '''
Model:
	things*=Thing+
;

Thing:
	'thing' name=ID '{'
	inner*=[Thing]*
	'}'
;
    '''


class Thing(object):
    def __init__(self, **kwargs):
        for k in kwargs.keys():
            setattr(self, k, kwargs[k])


def test_buildins():
    """
    This test is used to check if a model with buildins works correctly.
    The test uses no special scoping.

    The test loads
    - one model w/o buildins
    - one model with buildins
    - one model with unknown references (errors)
    """
    #################################
    # META MODEL DEF
    #################################

    type_builtins = {
        'OneThing': Thing(name="OneThing"),
        'OtherThing': Thing(name="OtherThing")
    }
    my_metamodel = metamodel_from_str(metamodel_str, classes=[Thing],builtins=type_builtins)

    #################################
    # MODEL PARSING
    #################################

    _ = my_metamodel.model_from_str('''
    thing A {}
    thing B {}
    thing C {A B}
    ''')


    _ = my_metamodel.model_from_str('''
    thing A {}
    thing B {}
    thing C {A B OneThing OtherThing}
    ''')

    with raises(textx.exceptions.TextXSemanticError, match=r'.*Unknown object.*UnknownPart.*'):
        _ = my_metamodel.model_from_str('''
        thing A {}
        thing B {}
        thing C {A B OneThing OtherThing UnknownPart}
        ''')

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
    """
    #################################
    # META MODEL DEF
    #################################

    type_builtins = {
        'OneThing': Thing(name="OneThing"),
        'OtherThing': Thing(name="OtherThing")
    }
    my_metamodel = metamodel_from_str(metamodel_str, classes=[Thing],builtins=type_builtins)
    my_metamodel.register_scope_provider({"*.*": scoping.scope_provider_fully_qualified_names})

    #################################
    # MODEL PARSING
    #################################

    _ = my_metamodel.model_from_str('''
    thing A {}
    thing B {}
    thing C {A B}
    ''')


    _ = my_metamodel.model_from_str('''
    thing A {}
    thing B {}
    thing C {A B OneThing OtherThing}
    ''')

    with raises(textx.exceptions.TextXSemanticError, match=r'.*Unknown object.*UnknownPart.*'):
        _ = my_metamodel.model_from_str('''
        thing A {}
        thing B {}
        thing C {A B OneThing OtherThing UnknownPart}
        ''')

    #################################
    # END
    #################################
