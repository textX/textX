from dataclasses import dataclass
from os.path import abspath, dirname, join

from pytest import raises

import textx.scoping.providers as scoping_providers
from textx import (
    get_children_of_type,
    get_model,
    metamodel_from_file,
    metamodel_from_str,
    textx_isinstance,
)
from textx.scoping.tools import (
    get_list_of_concatenated_objects,
    get_unique_named_object,
    resolve_model_path,
)


def test_textx_tools_with_frozen_classes1():
    @dataclass(frozen=True)
    class Model:
        # _tx_filename: object
        # _tx_parser: object
        use: object
        data: object

    @dataclass(frozen=True)
    class Content:
        parent: object
        elementsA: object
        elementsB: object
        ref: object

    @dataclass(frozen=True)
    class Element:
        parent: object
        name: object

    grammar = r"""
    Model:
        'use' use=Use
        data=Content;
    Content:
        'A:' elementsA+=Element
        'B:' elementsB+=Element
        'ref' ref=[Element];
    Element: '*' name=ID;
    Use: 'A'|'B';
    """
    text_ok1 = r"""
        use A
        A: *a *b *c
        B: *d *e *f
        ref b
    """
    text_ok2 = r"""
        use B
        A: *a *b *c
        B: *d *e *f
        ref d
    """
    text_not_ok = r"""
        use B
        A: *a *b *c
        B: *d *e *f
        ref b
    """
    for classes in [[], [Model, Content, Element]]:
        print("Test Loop, classes==", classes)

        ref_scope_was_used = False

        def ref_scope(refItem, myattr, attr_ref):
            # python3: nonlocal ref_scope_was_used
            nonlocal ref_scope_was_used
            ref_scope_was_used = True
            if get_model(refItem).use == "A":
                return resolve_model_path(
                    refItem, f"parent(Model).data.elementsA.{attr_ref.obj_name}", True
                )
            else:
                return resolve_model_path(
                    refItem, f"parent(Model).data.elementsB.{attr_ref.obj_name}", True
                )

        mm = metamodel_from_str(grammar, classes=classes)
        mm.register_scope_providers({"Content.ref": ref_scope})
        ref_scope_was_used = False
        m = mm.model_from_str(text_ok1)
        assert ref_scope_was_used
        if len(classes) == 0:
            # Assert that model object has its own filename and metamodel
            assert "_tx_filename" in m.__dict__
            assert "_tx_metamodel" in m.__dict__
        else:
            # Assert that special attributes are accessible only through class
            assert "_tx_filename" not in m.__dict__
            assert "_tx_metamodel" not in m.__dict__

        ref_scope_was_used = False
        mm.model_from_str(text_ok2)
        assert ref_scope_was_used

        ref_scope_was_used = False
        with raises(Exception, match=r'.*Unknown object "b".*'):
            mm.model_from_str(text_not_ok)
        assert ref_scope_was_used


def test_textx_tools_with_frozen_classes2():
    class Model:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    @dataclass(frozen=True)
    class Content:
        parent: object
        elementsA: object
        elementsB: object
        ref: object

    @dataclass(frozen=True)
    class Element:
        parent: object
        name: object

    grammar = r"""
    Model:
        'use' use=Use
        data=Content;
    Content:
        'A:' elementsA+=Element
        'B:' elementsB+=Element
        'ref' ref=[Element];
    Element: '*' name=ID;
    Use: 'A'|'B';
    """
    text_ok1 = r"""
        use A
        A: *a *b *c
        B: *d *e *f
        ref b
    """
    text_ok2 = r"""
        use B
        A: *a *b *c
        B: *d *e *f
        ref d
    """
    text_not_ok = r"""
        use B
        A: *a *b *c
        B: *d *e *f
        ref b
    """
    for classes in [[], [Model, Content, Element]]:
        print("Test Loop, classes==", classes)

        ref_scope_was_used = False

        def ref_scope(refItem, myattr, attr_ref):
            # python3: nonlocal ref_scope_was_used
            nonlocal ref_scope_was_used
            ref_scope_was_used = True
            if get_model(refItem).use == "A":
                return resolve_model_path(
                    refItem, f"parent(Model).data.elementsA.{attr_ref.obj_name}", True
                )
            else:
                return resolve_model_path(
                    refItem, f"parent(Model).data.elementsB.{attr_ref.obj_name}", True
                )

        mm = metamodel_from_str(grammar, classes=classes)
        mm.register_scope_providers({"Content.ref": ref_scope})
        ref_scope_was_used = False
        m = mm.model_from_str(text_ok1)
        assert ref_scope_was_used

        assert hasattr(m, "_tx_filename")
        assert hasattr(m, "_tx_metamodel")

        ref_scope_was_used = False
        mm.model_from_str(text_ok2)
        assert ref_scope_was_used

        ref_scope_was_used = False
        with raises(Exception, match=r'.*Unknown object "b".*'):
            mm.model_from_str(text_not_ok)
        assert ref_scope_was_used


def test_textx_isinstance():
    grammar = """
    Model: a=A;
    A: B;
    B: C;
    C: x=ID;
    """
    my_meta_model = metamodel_from_str(grammar)
    A = my_meta_model["A"]
    B = my_meta_model["B"]
    C = my_meta_model["C"]
    my_model = my_meta_model.model_from_str("c")
    c = get_children_of_type("C", my_model)
    assert len(c) == 1
    c = c[0]
    assert textx_isinstance(c, C)
    assert textx_isinstance(c, B)
    assert textx_isinstance(c, A)


def test_resolve_model_path_with_lists():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "components_model1", "Components.tx")
    )
    my_meta_model.register_scope_providers(
        {
            "*.*": scoping_providers.FQN(),
            "Connection.from_port": scoping_providers.ExtRelativeName(
                "from_inst.component", "slots", "extends"
            ),
            "Connection.to_port": scoping_providers.ExtRelativeName(
                "to_inst.component", "slots", "extends"
            ),
        }
    )

    #################################
    # MODEL PARSING
    #################################

    my_model = my_meta_model.model_from_file(
        join(
            abspath(dirname(__file__)), "components_model1", "example_inherit2.components"
        )
    )

    #################################
    # TEST MODEL
    #################################

    action2a = resolve_model_path(my_model, "packages.usage.instances.action2", True)
    action2b = get_unique_named_object(my_model, "action2")
    assert action2a is action2b

    middle_a = resolve_model_path(my_model, "packages.base.components.Middle", True)
    middle_b = get_unique_named_object(my_model, "Middle")
    assert middle_a is middle_b

    # test parent(...) with lists
    action2a_with_parent = resolve_model_path(
        action2a, "parent(Model).packages.usage.instances.action2", True
    )
    assert action2a_with_parent == action2a

    # test "normal" parent with lists
    action2a_with_parent2 = resolve_model_path(action2a, "parent.instances.action2", True)
    assert action2a_with_parent2 == action2a

    with raises(
        Exception, match=r".*unexpected: got list in path for " r"get_referenced_object.*"
    ):
        resolve_model_path(my_model, "packages.usage.instances.action2", False)


def test_resolve_model_path_simple_case():
    #################################
    # META MODEL DEF
    #################################

    grammar = r"""
        Model: name=ID a=A b=B;
        A: 'A:' name=ID;
        B: 'B:' name=ID ('->' b=B| '=' a=A );
    """

    mm = metamodel_from_str(grammar)

    #################################
    # MODEL PARSING
    #################################

    model = mm.model_from_str(
        r"""
        My_Model
            A: OuterA
            B: Level0_B
             -> B: Level1_B
             -> B: Level2_B
             = A: InnerA
    """
    )

    #################################
    # TEST MODEL
    #################################

    # test normal functionality
    outerA = resolve_model_path(model, "a")
    assert outerA.name == "OuterA"
    level0B = resolve_model_path(model, "b")
    assert level0B.name == "Level0_B"
    level1B = resolve_model_path(model, "b.b")
    assert level1B.name == "Level1_B"
    level2B = resolve_model_path(model, "b.b.b")
    assert level2B.name == "Level2_B"
    innerA = resolve_model_path(model, "b.b.b.a")
    assert innerA.name == "InnerA"

    # test parent(TYPE)
    outerA2 = resolve_model_path(model, "b.b.b.parent(Model).a")
    assert outerA2 == outerA

    # test "normal" parent
    outerA3 = resolve_model_path(model, "b.b.parent.parent.a")
    assert outerA3 == outerA

    # test "None"
    level3B_none = resolve_model_path(model, "b.b.b.b")
    assert level3B_none is None
    innerA_none1 = resolve_model_path(model, "b.b.b.b.a")
    assert innerA_none1 is None
    innerA_none2 = resolve_model_path(model, "b.b.a")
    assert innerA_none2 is None


def test_resolve_model_path_simple_case_with_refs():
    #################################
    # META MODEL DEF
    #################################

    grammar = r"""
        Model: name=ID b=B;
        B: 'B:' name=ID ('->' b=B | '-->' bref=[B] );
    """

    mm = metamodel_from_str(grammar)

    #################################
    # MODEL PARSING
    #################################

    model = mm.model_from_str(
        r"""
        My_Model
            B: Level0_B
             -> B: Level1_B
             --> Level0_B
    """
    )

    #################################
    # TEST MODEL
    #################################

    # test normal functionality (with refs)
    level0B = resolve_model_path(model, "b")
    assert level0B.name == "Level0_B"
    level1B = resolve_model_path(model, "b.b")
    assert level1B.name == "Level1_B"
    bref = resolve_model_path(model, "b.b.bref")
    assert bref.name == "Level0_B"
    assert bref == level0B


def test_get_list_of_concatenated_objects():
    #################################
    # META MODEL DEF
    #################################

    my_meta_model = metamodel_from_file(
        join(abspath(dirname(__file__)), "components_model1", "Components.tx")
    )
    my_meta_model.register_scope_providers(
        {
            "*.*": scoping_providers.FQN(),
            "Connection.from_port": scoping_providers.ExtRelativeName(
                "from_inst.component", "slots", "extends"
            ),
            "Connection.to_port": scoping_providers.ExtRelativeName(
                "to_inst.component", "slots", "extends"
            ),
        }
    )

    #################################
    # MODEL PARSING
    #################################

    my_model1 = my_meta_model.model_from_file(
        join(
            abspath(dirname(__file__)), "components_model1", "example_inherit1.components"
        )
    )
    my_model2 = my_meta_model.model_from_file(
        join(
            abspath(dirname(__file__)), "components_model1", "example_inherit2.components"
        )
    )

    #################################
    # TEST MODEL
    #################################

    # test extends A,B
    start = get_unique_named_object(my_model1, "Start")
    middle = get_unique_named_object(my_model1, "Middle")
    end = get_unique_named_object(my_model1, "End")
    inherited_classes = get_list_of_concatenated_objects(middle, "extends")
    assert len(inherited_classes) == 3
    assert inherited_classes[0] is middle
    assert inherited_classes[1] is start
    assert inherited_classes[2] is end

    # test extends A extends B
    start = get_unique_named_object(my_model2, "Start")
    middle = get_unique_named_object(my_model2, "Middle")
    end = get_unique_named_object(my_model2, "End")
    inherited_classes = get_list_of_concatenated_objects(middle, "extends")
    assert len(inherited_classes) == 3
    assert inherited_classes[0] is middle
    assert inherited_classes[1] is start
    assert inherited_classes[2] is end
