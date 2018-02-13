from textx import metamodel_from_str
from textx import get_children
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

    my_model = my_metamodel.model_from_str('''
    thing A {}
    thing B {}
    thing C {A B}
    ''')


    my_model = my_metamodel.model_from_str('''
    thing A {}
    thing B {}
    thing C {A B OneThing OtherThing}
    ''')

    with raises(textx.exceptions.TextXSemanticError, match=r'.*Unknown object.*UnknownPart.*'):
        my_model = my_metamodel.model_from_str('''
        thing A {}
        thing B {}
        thing C {A B OneThing OtherThing UnknownPart}
        ''')

    #################################
    # END
    #################################

def test_buildins_fully_qualified_name():
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

    my_model = my_metamodel.model_from_str('''
    thing A {}
    thing B {}
    thing C {A B}
    ''')


    my_model = my_metamodel.model_from_str('''
    thing A {}
    thing B {}
    thing C {A B OneThing OtherThing}
    ''')

    with raises(textx.exceptions.TextXSemanticError, match=r'.*Unknown object.*UnknownPart.*'):
        my_model = my_metamodel.model_from_str('''
        thing A {}
        thing B {}
        thing C {A B OneThing OtherThing UnknownPart}
        ''')

    #################################
    # END
    #################################
