from textx import metamodel_from_str
from pytest import raises
import textx.exceptions


def test_referencing_attributes():
    """
    The key idea is that the list of references to "Val"s in the
    "Reference"s can have any size>0 and contains not directly references
    to objects, but helper objects ("RefItem"s) that contain the desired
    references.
    With this, the list "refs" to "RefItem"s in the "Reference" object is
    build completely during initial parsing. The references inside the
    "RefItem"s, can the be resolved on after the other...
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

    def ref_scope(refItem, attr, attr_ref):
        from textx.scoping.tools import get_referenced_object
        from textx.scoping import Postponed
        reference = refItem.parent
        if reference is None:
            return Postponed()
        index = reference.refs.index(refItem)
        assert (index >= 0)
        if index == 0:
            return get_referenced_object(
                None, reference,
                "instance.type.vals.{}".format(attr_ref.obj_name),
                attr_ref.cls)
        else:
            return get_referenced_object(
                None, reference.refs[index - 1],
                "valref.type.vals.{}".format(attr_ref.obj_name),
                attr_ref.cls)

    mm = metamodel_from_str(grammar)
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
                match=r'.*Unknown object.*x.*'):
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
