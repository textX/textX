from __future__ import unicode_literals
from textx.scoping.rrel import rrel_standalone, parse
from arpeggio import ParserPython
from textx import metamodel_from_str
from textx.scoping.rrel import find


def test_rrel_basic_parser1():
    parser = ParserPython(rrel_standalone)
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
    tree = parse("a,b,c")
    assert str(tree) == 'a,b,c'


metamodel_str = '''
    Model:
        packages*=Package
    ;

    Package:
        'package' name=ID '{'
        packages*=Package
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

modeltext = '''
    package P1 {
        class Part1 {
        }
    }
    package P2 {
        package Inner {
            class Inner {
                attr inner;
            }
        }
        class Part2 {
            attr rec;
        }
        class C2 {
            attr p1;
            attr p2a;
            attr p2b;
        }
        class rec {
            attr p1;
        }
    }
    '''


def test_rrel_basic_lookup():
    """
    This is a basic test for the find function:
    we use a model with some structure
    and query this structure with RREL expressions.
    """
    #################################
    # META MODEL DEF
    #################################

    my_metamodel = metamodel_from_str(metamodel_str)

    #################################
    # MODEL PARSING
    #################################

    my_model = my_metamodel.model_from_str(modeltext)

    #################################
    # TEST
    #################################

    P2 = find(my_model, "P2", "packages")
    assert P2 is not None
    Part2 = find(my_model, "P2.Part2", "packages.classes")
    assert Part2 is not None
    rec = find(my_model, "P2.Part2.rec", "packages.classes.attributes")
    assert rec is not None

    P2 = find(my_model, "P2", "(packages)")
    assert P2 is not None

    from textx import get_model
    assert get_model(my_model) is my_model

    P2 = find(my_model, "P2", "packages*")
    assert P2 is not None
    Part2 = find(my_model, "P2.Part2", "packages*.classes")
    assert Part2 is not None
    rec = find(my_model, "P2.Part2.rec", "packages*.classes.attributes")
    assert rec is not None

    Part2_tst = find(rec, "", "..")
    assert Part2_tst is not None
    assert Part2_tst is Part2

    P2_from_inner_node = find(rec, "P2", "(packages)")
    assert P2_from_inner_node is P2

    P2_tst = find(rec, "", "parent(Package)")
    assert P2_tst is not None
    assert P2_tst is P2

    P2_tst = find(rec, "", "...")
    assert P2_tst is not None
    assert P2_tst is P2

    P2_tst = find(rec, "", ".(..).(..)")
    assert P2_tst is not None
    assert P2_tst is P2

    P2_tst = find(rec, "", "(..).(..)")
    assert P2_tst is not None
    assert P2_tst is P2

    P2_tst = find(rec, "", "...(.).(.)")
    assert P2_tst is not None
    assert P2_tst is P2

    P2_tst = find(rec, "", "..(.).(..)")
    assert P2_tst is not None
    assert P2_tst is P2

    P2_tst = find(rec, "", "..((.)*)*.(..)")
    assert P2_tst is not None
    assert P2_tst is P2

    none = find(my_model, "", "..")
    assert none is None

    inner = find(my_model, "inner", "~packages.~packages.~classes.attributes")
    assert inner is not None
    assert inner.name == "inner"

    # expensive version of a "Plain Name" scope provider:
    inner = find(my_model, "inner", "~packages*.~classes.attributes")
    assert inner is not None
    assert inner.name == "inner"

    rec2 = find(my_model, "P2.Part2.rec", "other1,other2,packages*.classes.attributes")
    assert rec2 is rec

    rec2 = find(my_model, "P2.Part2.rec", "other1,packages*.classes.attributes,other2")
    assert rec2 is rec

    rec2 = find(my_model, "P2.Part2.rec", "other1,other2,other3")
    assert rec2 is None

    rec2 = find(my_model, "P2.Part2.rec", "(packages,classes,attributes)*")
    assert rec2 is rec

    rec2 = find(my_model, "P2.Part2.rec", "(packages,(classes,attributes)*)*.attributes")
    assert rec2 is rec

    rec2 = find(my_model, "rec", "(~packages,~classes,attributes,classes)*")
    assert rec2 is not None

    rec2 = find(my_model, "rec",
                "(~packages,~classes,attributes,classes)*", my_metamodel["OBJECT"])
    assert rec2 is not None

    rec2 = find(my_model, "rec",
                "(~packages,~classes,attributes,classes)*", my_metamodel["Attribute"])
    assert rec2 is rec

    rec2 = find(my_model, "rec",
                "(~packages,~classes,attributes,classes)*", my_metamodel["Package"])
    assert rec2 is None

    rec2 = find(my_model, "rec",
                "(~packages,classes,attributes,~classes)*", my_metamodel["Class"])
    assert rec2 is not None
    assert rec2 is not rec  # it is the class...

    rec2 = find(my_model, "rec",
                "(~packages,~classes,attributes,classes)*", my_metamodel["Class"])
    assert rec2 is not None
    assert rec2 is not rec  # it is the class...

    t = find(my_model, "", ".")
    assert t is my_model

    t = find(my_model, "", "(.)")
    assert t is my_model

    t = find(my_model, "", "(.)*")
    assert t is my_model

    t = find(my_model, "", "(.)*.no_existent")  # inifite recursion stopper
    assert t is None

    rec2 = find(my_model, "rec",
                "(.)*.(~packages,~classes,attributes,classes)*", my_metamodel["Class"])
    assert rec2 is not None
    assert rec2 is not rec  # it is the class...

    # Here, we test the start_from_root/start_locally logic:
    P2t = find(rec, "P2", "(.)*.packages")
    assert P2t is None
    P2t = find(rec, "P2", "(.,not_existent_but_root)*.packages")
    assert P2t is P2
    rect = find(rec, "rec", "(~packages)*.(..).attributes")
    assert rect is None
    rect = find(rec, "rec", "(.,~packages)*.(..).attributes")
    assert rect is rec


def test_rrel_repetitions():
    """
    This is a basic extra test to demonstrate `()*`
    in RREL expressions.
    """

    my_metamodel = metamodel_from_str(r'''
        Model: entries*=Entry;
        Entry: name=ID (':' ref=[Entry])?;
    ''')

    my_model = my_metamodel.model_from_str(r'''
        a: b
        c
        b: a
    ''')

    a = find(my_model, "a", "entries.ref*")
    assert a.name == 'a'
    b = find(my_model, "b", "entries.ref*")
    assert b.name == 'b'
    c = find(my_model, "c", "entries.ref*")
    assert c.name == 'c'

    a2 = find(my_model, "a.b.a", "entries.ref*")
    assert a2 == a

    b2 = find(my_model, "b.a.b", "entries.ref*")
    assert b2 == b

    a2 = find(my_model, "b.a.b.a", "entries.ref*")
    assert a2 == a

    a2 = find(my_model, "b.a.b.a.b.a.b.a.b.a", "entries.ref*")
    assert a2 == a
