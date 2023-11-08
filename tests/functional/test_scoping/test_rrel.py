from arpeggio import NoMatch, ParserPython
from pytest import raises

from textx import metamodel_from_str, textx_isinstance
from textx.exceptions import TextXSemanticError
from textx.scoping import ModelRepository
from textx.scoping.rrel import find, find_object_with_path, parse, rrel_standalone


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
    assert str(tree) == "(..)*.(pkg)*.cls"
    tree = parse("obj.ref.~extension *.methods")
    assert str(tree) == "obj.ref.(~extension)*.methods"
    tree = parse("type.vals")
    assert str(tree) == "type.vals"
    tree = parse("(type.vals)")
    assert str(tree) == "(type.vals)"
    tree = parse("(type.vals)*")
    assert str(tree) == "(type.vals)*"
    tree = parse("instance . ( type.vals ) *")
    assert str(tree) == "instance.(type.vals)*"
    tree = parse("a,b,c")
    assert str(tree) == "a,b,c"
    tree = parse("a.b.c")
    assert str(tree) == "a.b.c"
    tree = parse("parent(NAME)")
    assert str(tree) == "parent(NAME)"
    tree = parse("a.'b'~b.'c'~x")
    assert str(tree) == "a.'b'~b.'c'~x"

    # do not allow "empty" rrel expressions:
    with raises(NoMatch):
        tree = parse("")
    with raises(NoMatch):
        tree = parse("a,b,c,")


metamodel_str = """
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
    """

modeltext = """
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
    """


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
    assert P2.name == "P2"
    Part2 = find(my_model, "P2.Part2", "packages.classes")
    assert Part2.name == "Part2"
    rec = find(my_model, "P2.Part2.rec", "packages.classes.attributes")
    rec_with_fixed_name = find(my_model, "P2.rec", "packages.'Part2'~classes.attributes")
    assert rec_with_fixed_name is rec
    assert rec.name == "rec"
    assert rec.parent == Part2

    P2 = find(my_model, "P2", "(packages)")
    assert P2.name == "P2"

    from textx import get_model

    assert get_model(my_model) is my_model

    P2 = find(my_model, "P2", "packages*")
    assert P2.name == "P2"
    Part2 = find(my_model, "P2.Part2", "packages*.classes")
    assert Part2.name == "Part2"
    rec = find(my_model, "P2.Part2.rec", "packages*.classes.attributes")
    assert rec.name == "rec"
    assert rec.parent == Part2

    Part2_tst = find(rec, "", "..")
    assert Part2_tst is Part2

    P2_from_inner_node = find(rec, "P2", "(packages)")
    assert P2_from_inner_node is P2

    P2_tst = find(rec, "", "parent(Package)")
    assert P2_tst is P2

    P2_tst = find(rec, "", "...")
    assert P2_tst is P2

    P2_tst = find(rec, "", ".(..).(..)")
    assert P2_tst is P2

    P2_tst = find(rec, "", "(..).(..)")
    assert P2_tst is P2

    P2_tst = find(rec, "", "...(.).(.)")
    assert P2_tst is P2

    P2_tst = find(rec, "", "..(.).(..)")
    assert P2_tst is P2

    P2_tst = find(rec, "", "..((.)*)*.(..)")
    assert P2_tst is P2

    none = find(my_model, "", "..")
    assert none is None

    m = find(my_model, "", ".")  # '.' references the current element
    assert m is my_model

    inner = find(my_model, "inner", "~packages.~packages.~classes.attributes")
    assert inner.name == "inner"

    package_Inner = find(inner, "Inner", "parent(OBJECT)*.packages")
    assert textx_isinstance(package_Inner, my_metamodel["Package"])
    assert not textx_isinstance(package_Inner, my_metamodel["Class"])

    assert None is find(inner, "P2", "parent(Class)*.packages")

    # expensive version of a "Plain Name" scope provider:
    inner = find(my_model, "inner", "~packages*.~classes.attributes")
    assert inner.name == "inner"

    rec2 = find(my_model, "P2.Part2.rec", "other1,other2,packages*.classes.attributes")
    assert rec2 is rec

    rec2 = find(my_model, "P2.Part2.rec", "other1,packages*.classes.attributes,other2")
    assert rec2 is rec

    rec2 = find(
        my_model,
        "P2::Part2::rec",
        "other1,packages*.classes.attributes,other2",
        split_string="::",
    )
    assert rec2 is rec

    rec2 = find(my_model, "P2.Part2.rec", "other1,other2,other3")
    assert rec2 is None

    rec2 = find(my_model, "P2.Part2.rec", "(packages,classes,attributes)*")
    assert rec2 is rec

    rec2 = find(my_model, "P2.Part2.rec", "(packages,(classes,attributes)*)*.attributes")
    assert rec2 is rec

    rec2 = find(my_model, "rec", "(~packages,~classes,attributes,classes)*")
    assert rec2.name == "rec"

    rec2 = find(
        my_model,
        "rec",
        "(~packages,~classes,attributes,classes)*",
        my_metamodel["OBJECT"],
    )
    assert rec2.name == "rec"

    rec2 = find(
        my_model,
        "rec",
        "(~packages,~classes,attributes,classes)*",
        my_metamodel["Attribute"],
    )
    assert rec2 is rec

    rec2 = find(
        my_model,
        "rec",
        "(~packages,~classes,attributes,classes)*",
        my_metamodel["Package"],
    )
    assert rec2 is None

    rec2 = find(
        my_model, "rec", "(~packages,classes,attributes,~classes)*", my_metamodel["Class"]
    )
    assert rec2.name == "rec"
    assert rec2 is not rec  # it is the class...

    rec2 = find(
        my_model, "rec", "(~packages,~classes,attributes,classes)*", my_metamodel["Class"]
    )
    assert rec2.name == "rec"
    assert rec2 is not rec  # it is the class...

    t = find(my_model, "", ".")
    assert t is my_model

    t = find(my_model, "", "(.)")
    assert t is my_model

    t = find(my_model, "", "(.)*")
    assert t is my_model

    t = find(my_model, "", "(.)*.no_existent")  # inifite recursion stopper
    assert t is None

    rec2 = find(
        my_model,
        "rec",
        "(.)*.(~packages,~classes,attributes,classes)*",
        my_metamodel["Class"],
    )
    assert rec2.name == "rec"
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

    my_metamodel = metamodel_from_str(
        r"""
        Model: entries*=Entry;
        Entry: name=ID (':' ref=[Entry])?;
    """
    )

    my_model = my_metamodel.model_from_str(
        r"""
        a: b
        c
        b: a
    """
    )

    a = find(my_model, "a", "entries.ref*")
    assert a.name == "a"
    b = find(my_model, "b", "entries.ref*")
    assert b.name == "b"
    c = find(my_model, "c", "entries.ref*")
    assert c.name == "c"

    a2 = find(my_model, "a.b.a", "entries.ref*")
    assert a2 == a

    b2 = find(my_model, "b.a.b", "entries.ref*")
    assert b2 == b

    res, objpath = find_object_with_path(my_model, "b.a.b", "entries.ref*")
    assert res == b
    assert len(objpath) == 3
    assert objpath[-1] == res
    assert ".".join(map(lambda x: x.name, objpath)) == "b.a.b"

    a2 = find(my_model, "b.a.b.a", "entries.ref*")
    assert a2 == a

    res, objpath = find_object_with_path(my_model, "b.a.b.a", "entries.ref*")
    assert res == a
    assert len(objpath) == 4
    assert objpath[-1] == res
    assert ".".join(map(lambda x: x.name, objpath)) == "b.a.b.a"

    a2 = find(my_model, "b.a.b.a.b.a.b.a.b.a", "entries.ref*")
    assert a2 == a


def test_split_str():
    from textx import metamodel_from_str

    mm = metamodel_from_str(
        """
        Model: a+=A r+=R;
        A: 'A' name=ID '{' a*=A  '}';
        R: 'R' a+=[A:FQN|+p:a*][','];
        FQN[split='::']: ID ('::' ID)*;
    """
    )
    m = mm.model_from_str(
        """
        A a1 {
            A aa1 {
                A aaa1 {}
                A aab1 {}
            }
        }
        A a2 {
            A aa2 {}
        }
        A R {
            A r2 {}
        }
        R a1::aa1::aaa1, a1::aa1::aab1, R, R::r2
        R R
        R a2::aa2
    """
    )
    assert len(m.r) == 3

    assert len(m.r[0].a) == 4
    assert len(m.r[1].a) == 1
    assert len(m.r[2].a) == 1

    assert ".".join(map(lambda x: x.name, m.r[0].a[0]._tx_path)) == "a1.aa1.aaa1"
    assert ".".join(map(lambda x: x.name, m.r[0].a[1]._tx_path)) == "a1.aa1.aab1"
    assert ".".join(map(lambda x: x.name, m.r[0].a[2]._tx_path)) == "R"
    assert ".".join(map(lambda x: x.name, m.r[0].a[3]._tx_path)) == "R.r2"

    with raises(TextXSemanticError, match=r".*Unknown object.*a2::unknown.*"):
        _ = mm.model_from_str(
            """
            A a1 {
                A aa1 {
                    A aaa1 {}
                    A aab1 {}
                }
            }
            A a2 {
                A aa2 {}
            }
            R a2::unknown
        """
        )


def test_split_str_multifile():
    # same as test above, but with "+mp:" flag
    from os.path import dirname, join

    from textx import metamodel_from_file

    this_folder = dirname(__file__)
    mm = metamodel_from_file(join(this_folder, "rrel", "Grammar.tx"))
    m = mm.model_from_file(join(this_folder, "rrel", "main.model"))
    # see above:
    assert ".".join(map(lambda x: x.name, m.r[0].a[0]._tx_path)) == "a1.aa1.aaa1"


def test_rrel_with_fixed_string_in_navigation():
    builtin_models = ModelRepository()
    mm = metamodel_from_str(
        r"""
        Model: types_collection*=TypesCollection
            ('activeTypes' '=' active_types=[TypesCollection])? usings*=Using;
        Using: 'using' name=ID "=" type=[Type:ID|+m:
                ~active_types.types,             // "regular lookup"
                'builtin'~types_collection.types // "default lookup"
                                                 // name "builtin" hard coded in grammar
            ];
        TypesCollection: 'types' name=ID "{" types*=Type "}";
        Type: 'type' name=ID;
        Comment: /#.*?$/;
    """,
        builtin_models=builtin_models,
    )

    builtin_models.add_model(
        mm.model_from_str(
            r"""
        types builtin {
            type i32
            type i64
            type f32
            type f64
        }
    """
        )
    )

    _ = mm.model_from_str(
        r"""
        types MyTypes {
            type Int
            type Double
        }
        types OtherTypes {
            type Foo
            type Bar
        }
        activeTypes=MyTypes
        using myDouble = Double
        using myInt = Int    # found via "regular lookup"
        using myi32 = i32    # found via "default lookup"
        # using myFoo = Foo  # --> not found
    """
    )

    with raises(TextXSemanticError, match=r'.*Unknown object "Foo".*'):
        _ = mm.model_from_str(
            r"""
            types MyTypes {
                type Int
                type Double
            }
            types OtherTypes {
                type Foo
                type Bar
            }
            activeTypes=MyTypes
            using myDouble = Double
            using myInt = Int    # found via "regular lookup"
            using myi32 = i32    # found via "default lookup"
            using myFoo = Foo    # --> not found
        """
        )


def test_rrel_with_fixed_string_in_navigation_with_scalars():
    builtin_models = ModelRepository()
    mm = metamodel_from_str(
        r"""
        Model: types_collection=TypesCollection // scalar here (compared to last test)
            ('activeTypes' '=' active_types=[TypesCollection])? usings*=Using;
        Using: 'using' name=ID "=" type=[Type:ID|+m:
                ~active_types.types,             // "regular lookup"
                'builtin'~types_collection.types // "default lookup"
                                                 // name "builtin" hard coded in grammar
            ];
        TypesCollection: 'types' name=ID "{" types*=Type "}";
        Type: 'type' name=ID;
        Comment: /#.*?$/;
    """,
        builtin_models=builtin_models,
    )

    builtin_models.add_model(
        mm.model_from_str(
            r"""
        types builtin {
            type i32
            type i64
            type f32
            type f64
        }
    """
        )
    )

    _ = mm.model_from_str(
        r"""
        types MyTypes {
            type Int
            type Double
        }
        activeTypes=MyTypes
        using myDouble = Double
        using myInt = Int    # found via "regular lookup"
        using myi32 = i32    # found via "default lookup"
    """
    )

    with raises(TextXSemanticError, match=r'.*Unknown object "Unknown".*'):
        _ = mm.model_from_str(
            r"""
            types MyTypes {
                type Int
                type Double
            }
            activeTypes=MyTypes
            using myDouble = Double
            using myInt = Int    # found via "regular lookup"
            using myi32 = i32    # found via "default lookup"
            using myFoo = Unknown    # --> not found
        """
        )


def test_lookup_multifile():
    # same as test above, but with "+mp:" flag
    from os.path import dirname, join

    from textx import metamodel_from_file

    this_folder = dirname(__file__)
    mm = metamodel_from_file(join(this_folder, "rrel_multifile", "Grammar.tx"))

    # "standard" multi-file usage
    m = mm.model_from_file(join(this_folder, "rrel_multifile", "main.model"))
    assert m is not None

    # Rule "P1" employs a mandatory rrel path entry ".." (no multi-file)
    m = mm.model_from_file(join(this_folder, "rrel_multifile", "navigation0.model"))
    assert m is not None

    # Rule "P1" employs a mandatory rrel path entry ".." (with multi-file)
    # Note: "+pm:..(..)*.a*" works with the current impl (TODO: remove comment)
    # TODO: in case of multi-files, do not start at the root of each model, but
    # iterate over all models once the path reaches the model root (e.g. with .. in
    # a navigation rrel node)...
    m = mm.model_from_file(join(this_folder, "rrel_multifile", "navigation1.model"))
    assert m is not None

    # the next exammple is missing the include statement (leads to "Unknown object...")
    with raises(TextXSemanticError, match=r"Unknown object"):
        _ = mm.model_from_file(
            join(this_folder, "rrel_multifile", "navigation1_err.model")
        )


def test_lookup_multifile_missing_flag_m():
    from os.path import dirname, join

    from textx import metamodel_from_file

    this_folder = dirname(__file__)

    # the next exammple is missing the +m flag in the grammar
    # (lookup across files disabled):
    mmE = metamodel_from_file(
        join(this_folder, "rrel_multifile", "GrammarMissingPlusM.tx")
    )
    with raises(TextXSemanticError, match=r"Unknown object"):
        _ = mmE.model_from_file(join(this_folder, "rrel_multifile", "navigation1.model"))
