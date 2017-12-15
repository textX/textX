from textx.metamodel import metamodel_from_str
from textx.model import children, children_of_type
import textx.scoping as scoping
from operator import eq
import re

metamodel_str = '''
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
        'attr' ref=[Class|FQN] name=ID ';'
;

RefClass: ref=FQN;

FQN: ID('.'ID)*;
    '''

def test_fully_qualified_name_ref():
    #################################
    # META MODEL DEF
    #################################

    my_metamodel = metamodel_from_str(metamodel_str)


    my_metamodel.register_scope_provider({"*.*":scoping.scope_provider_fully_qualified_name})

    #################################
    # MODEL PARSING
    #################################

    my_model = my_metamodel.model_from_str('''
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
    ''')

    #################################
    # TEST 
    #################################

    res = children_of_type("Class", my_model)
    res.sort(key=lambda x: x.name)
    assert( len(res)==3 )
    assert( all(map(eq, map(lambda x:x.name, res), ["C2","Part1","Part2"])) );
    assert( not all(map(eq, map(lambda x:x.name, res), ["Part1","Part2","C2"])) );
    for x in res:
        assert(x.__class__.__name__ == "Class")
    
    res = children_of_type("Attribute", my_model)
    res.sort(key=lambda x: x.name)
    assert( len(res)==4 )
    assert( all(map(eq, map(lambda x:x.name, res), ["p1","p2a","p2b","rec"])) );
    for x in res:
        assert(x.__class__.__name__ == "Attribute")

    res = children(lambda x:hasattr(x,"name") and re.match(".*2.*", x.name), my_model)
    res.sort(key=lambda x: x.name)
    assert( len(res)==5 )
    assert( all(map(eq, map(lambda x:x.name, res), ["C2","P2","Part2","p2a","p2b"])) );

    #################################
    # END
    #################################

