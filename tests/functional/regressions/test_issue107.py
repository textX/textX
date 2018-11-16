import textx
import textx.scoping.providers
import textx.exceptions
from pytest import raises


def test_issue107_example_with_FQN_scoping_and_a_validator():
    grammar = '''
    Model:
        groupKind1 = GroupKind1?
        groupKind2 = GroupKind2?
        values += Ref+
    ;

    LiteralKind1Or2: LiteralKind1 | LiteralKind2;

    LiteralKind1 : name=ID;
    GroupKind1:
        "Kind1" name=ID "{"
            vars += LiteralKind1*
        "}"
    ;

    LiteralKind2 : name=ID;
    GroupKind2:
        "Kind2" name=ID "{"
            vars += LiteralKind2*
            ("/"
            error_vars += LiteralKind1*)?
        "}"
    ;

    Ref : val = [LiteralKind1Or2|FQN] ;

    FQN : ID'.'ID;
    '''
    mm = textx.metamodel_from_str(grammar)
    fqn = textx.scoping.providers.FQN()
    mm.register_scope_providers({"*.*": fqn})  # OK: "*.*" --> set default

    # =================================================
    # OPTIONAL
    #
    # make sure LiteralKind1 comes from GroupKind1 etc.

    def check_ref(ref):
        def check(ref, obj, typeof_parent):
            import textx.scoping.tools
            if obj.parent.__class__.__name__ != typeof_parent:
                raise textx.exceptions.TextXSemanticError(
                    "unexpected parent type {} for {}".format(
                        obj.parent.__class__.__name__,
                        obj.name
                    ), **textx.scoping.tools.get_location(ref))

        if ref.val.__class__.__name__ == "LiteralKind1":
            check(ref, ref.val, "GroupKind1")
        if ref.val.__class__.__name__ == "LiteralKind2":
            check(ref, ref.val, "GroupKind2")

    mm.register_obj_processors({"Ref": check_ref})

    #
    # =================================================

    model = '''
    Kind1 kind1 {
        a b c
    }
    Kind2 kind2 {
        a b c
    }

    kind1.a kind1.b kind2.a
    '''

    m = mm.model_from_str(model)

    assert m.values[0].val.parent == m.groupKind1
    assert m.values[1].val.parent == m.groupKind1
    assert m.values[2].val.parent == m.groupKind2

    model2 = '''
    Kind1 kind1 {
        a b c
    }
    Kind2 kind2 {
        a b c / This_is_a_kind1
    }

    kind1.a kind1.b kind2.a kind2.This_is_a_kind1
    '''

    with (raises(textx.exceptions.TextXSemanticError)):
        mm.model_from_str(model2)


def test_issue107_example_with_relative_name():
    grammar = '''
        Model:        kinds += GroupKind values += Ref;
        LiteralKind : name=ID;
        GroupKind:    kindName=ID name=ID "{"
                        vars *= LiteralKind
                      "}";
        Ref: ref0=[GroupKind] '.' ref1=[LiteralKind];
    '''
    mm = textx.metamodel_from_str(grammar)
    scope = textx.scoping.providers.RelativeName("ref0.vars")
    mm.register_scope_providers({"Ref.ref1": scope})

    model = '''
    Kind1 kind1 {
        a b c
    }
    Kind2 kind2 {
        a b c
    }

    kind1.a kind1.b kind2.a
    '''

    mm.model_from_str(model)


def test_issue107_example_with_relative_name_deep_tree():
    from textx.scoping.providers import RelativeName

    grammar = '''
        Model:        kinds += GroupKind values+=Formula;
        LiteralKind : name=ID;
        GroupKind:    kindName=ID name=ID "{"
                        vars *= LiteralKind
                      "}";
        Formula:      formula=FormulaPlus;
        FormulaPlus:  sum+=FormulaMult['+'];
        FormulaMult:  mul+=FormulaVal['*'];
        FormulaVal:   (ref=Ref)|(val=NUMBER)|('(' rec=FormulaPlus ')');
        Ref: ref0=[GroupKind] '.' ref1=[LiteralKind];
    '''
    mm = textx.metamodel_from_str(grammar)
    mm.register_scope_providers({
        "Ref.ref0": RelativeName("parent(Model).kinds"),
        "Ref.ref1": RelativeName("ref0.vars")
        })

    model = '''
    Kind1 kind1 {
        a b c
    }
    Kind2 kind2 {
        a b c
    }

    3+6*(7+2*kind1.a) 4+5*8(1+2*kind2.a) kind1.b
    '''
    mm.model_from_str(model)
