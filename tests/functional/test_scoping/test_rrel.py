from textx.scoping.rrel import rrel, parse
from arpeggio import ParserPython
from textx import metamodel_from_str
from textx.scoping.rrel import find

def test_rrel_basic_parser1():
    parser = ParserPython(rrel)
    parse_tree = parser.parse("^pkg*.cls")
    assert len(parse_tree) == 2  # always true (one path, one EOF)

    parse_tree = parser.parse("obj.ref.~extension *.methods")
    assert len(parse_tree) == 2  # always true (one path, one EOF)

    parse_tree = parser.parse("instance.(type.vals)*")
    assert len(parse_tree) == 2  # always true (one path, one EOF)


def test_rrel_basic_parser2():
    tree = parse("^pkg*.cls")
    assert str(tree) == '(..)*.(pkg)*.cls'
    tree = parse("obj.ref.~extension *.methods")
    assert str(tree) == 'obj.ref.(~extension)*.methods'
    tree = parse("type.vals")
    assert str(tree) == 'type.vals'
    tree = parse("(type.vals)")
    assert str(tree) == '(type.vals)'
    tree = parse("(type.vals)*")
    assert str(tree) == '(type.vals)*'
    tree = parse("instance . ( type.vals ) *")
    assert str(tree) == 'instance.(type.vals)*'


def test_rrel_basic_lookup():
    """
    This is a basic test for the find function
    """
    #################################
    # META MODEL DEF
    #################################
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
                'attr' name=ID ';'
        ;

        Comment: /#.*/;
        FQN: ID('.'ID)*;
        '''

    my_metamodel = metamodel_from_str(metamodel_str)

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
            attr rec;
        }
        class C2 {
            attr p1;
            attr p2a;
            attr p2b;
        }
    }
    ''')

    #################################
    # TEST MODEL
    #################################

    P2 = find(my_model, "P2", "packages")
    assert P2 is not None
    Part2 = find(my_model, "P2.Part2", "packages.classes")
    assert Part2 is not None
    rec = find(my_model, "P2.Part2.rec", "packages.classes.attributes")
    assert rec is not None

    P2 = find(my_model, "P2", "(packages)")
    assert P2 is not None

    P2 = find(my_model, "P2", "packages*")
    assert P2 is not None
    Part2 = find(my_model, "P2.Part2", "packages*.classes")
    assert Part2 is not None
    rec = find(my_model, "P2.Part2.rec", "packages*.classes.attributes")
    assert rec is not None
