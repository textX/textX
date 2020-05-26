from __future__ import unicode_literals
from textx import metamodel_from_str
from pytest import raises
import textx.exceptions
import attr


@attr.s(frozen=True)
class Instance(object):
    parent = attr.ib()
    name = attr.ib()
    type = attr.ib()


@attr.s(frozen=True)
class Reference(object):
    parent = attr.ib()
    instance = attr.ib()
    refs = attr.ib()


@attr.s(frozen=True)
class RefItem(object):
    parent = attr.ib()
    valref = attr.ib()


def test_referencing_attributes():
    """
    The key idea is that the list of references to "Val"s in the
    "Reference"s can have any size>0 and contains not directly references
    to objects, but helper objects ("RefItem"s) that contain the desired
    references.
    With this, the list "refs" to "RefItem"s in the "Reference" object is
    build completely during initial parsing. The references inside the
    "RefItem"s, can the be resolved on after the other...

    We also show how to handle custom classes here.
    """
    grammar = '''
    Model:
        structs+=Struct
        instances+=Instance
        references+=Reference;
    Struct:
        'struct' name=ID '{' vals+=Val '}';
    Val:
        'val' name=ID (':' type=[Struct])?;
    Instance:
        'instance' name=ID (':' type=[Struct])?;
    Reference:
        'reference' instance=[Instance] refs+=RefItem;
    RefItem:
        '.' valref=[Val];
    '''
    model_text = '''
    struct A {
        val x
    }
    struct B {
        val a: A
    }
    struct C {
        val b: B
        val a: A
    }
    struct D {
        val c: C
        val b1: B
        val a: A
    }
    instance d: D
    instance a: A
    reference d.c.b.a.x
    reference d.b1.a.x
    reference a.x
    '''

    for classes in [[], [Instance, Reference, RefItem]]:

        def ref_scope(refItem, myattr, attr_ref):
            from textx.scoping.tools import get_named_obj_in_list
            from textx.scoping import Postponed
            from textx import textx_isinstance

            reference = refItem.parent

            if reference is None:
                return Postponed()

            index = list(map(
                lambda x: id(x), reference.refs)).index(id(refItem))

            assert index >= 0

            base = reference.instance if index == 0 \
                else reference.refs[index - 1].valref
            if base is None or base.type is None:
                return Postponed()
            x = get_named_obj_in_list(base.type.vals, attr_ref.obj_name)
            if index == len(reference.refs) - 1:
                if not textx_isinstance(x, myattr.cls):
                    print(x)
                    return None

            return x

        mm = metamodel_from_str(grammar, classes=classes)
        mm.register_scope_providers({
            "RefItem.valref": ref_scope
        })
        m = mm.model_from_str(model_text)

        assert m.references[0].refs[-1].valref.name == 'x'
        assert m.references[0].refs[-1].valref == m.structs[0].vals[0]

        assert m.references[0].refs[-2].valref.name == 'a'
        assert m.references[0].refs[-2].valref == m.structs[1].vals[0]

        assert m.references[0].refs[-3].valref.name == 'b'
        assert m.references[0].refs[-3].valref == m.structs[2].vals[0]

        assert m.references[1].refs[-1].valref == m.structs[0].vals[0]

        assert m.references[2].refs[0].valref.name == 'x'
        assert m.references[2].refs[0].valref == m.structs[0].vals[0]

        # negative tests
        # error: "not_there" not pasrt of A
        with raises(textx.exceptions.TextXSemanticError,
                    match=r'.*Unknown object.*not_there.*'):
            mm.model_from_str('''
            struct A { val x }
            struct B { val a: A}
            struct C {
                val b: B
                val a: A
            }
            instance c: C
            reference c.b.a.not_there
            ''')

        # error: B.a is not of type A
        with raises(textx.exceptions.TextXSemanticError,
                    match=r'.*Unresolvable cross references.*x.*'):
            mm.model_from_str('''
            struct A { val x }
            struct B { val a }
            struct C {
                val b: B
                val a: A
            }
            instance c: C
            reference c.b.a.x
            ''')
