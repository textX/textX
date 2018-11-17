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


def test_issue107_example_with_relative_name_and_validation():
    """
        We model here:
         * Testcases
         * Aspects (to be tested)
         * Scenarios (for Testcases) with Configurations

        We want that only "Configurations" of the "Scenario"
        referenced by a "Testcase" are visible to the "Testcase".
        This restriction is context specific (to the context
        of the "Testcase" described by the referenced "Scenario").
        Scoping mechanisms allow to define this scope.
    """
    from textx import metamodel_from_str
    from textx.scoping.providers import RelativeName, FQN

    meta_model = metamodel_from_str(r'''
        Model: aspects+=Aspect scenarios+=Scenario testcases+=Testcase;
        Scenario: 'SCENARIO' name=ID 'BEGIN'
            configs+=Config
        'END';
        Config: 'CONFIG' name=ID 'HAS' '(' haves*=[Aspect] ')';
        Aspect: 'ASPECT' name=ID;
        Testcase: 'TESTCASE' name=ID 'BEGIN'
            'USES' scenario=[Scenario] 'WITH' config=[Config]
            'NEEDS' '(' needs*=[Aspect] ')'
        'END';
        Comment: /\/\/.*/;
    ''')

    # ------------------------------------
    # SCOPING
    #
    meta_model.register_scope_providers({
        '*.*': FQN(),

        # Here we define that the referenced configurations are
        # found in the referenced scenarios of a Testcase:
        'Testcase.config': RelativeName('scenario.configs')
    })

    # ------------------------------------
    # VALIDATION
    #
    def check_testcase(testcase):
        """
        checks that the config used by the testcase fulfills its needs
        """
        for need in testcase.needs:
            if need not in testcase.config.haves:
                raise textx.exceptions.TextXSemanticError(
                    "validation error: {}: {} not found in {}.{}".format(
                        testcase.name,
                        need.name,
                        testcase.scenario.name,
                        testcase.config.name
                    ))

    meta_model.register_obj_processors({
        'Testcase': check_testcase
    })

    # ------------------------------------
    # EXAMPLE
    #
    meta_model.model_from_str('''
        ASPECT NetworkTraffic
        ASPECT FileAccess
        SCENARIO S001 BEGIN
            CONFIG HeavyNetworkTraffic HAS (NetworkTraffic)
            CONFIG NoNetworkTraffic HAS ()
        END
        SCENARIO S002 BEGIN
            CONFIG WithFileAccess HAS (NetworkTraffic FileAccess)
            CONFIG NoFileAccess HAS (NetworkTraffic)
        END
        TESTCASE T001 BEGIN
            USES S001 WITH HeavyNetworkTraffic
            NEEDS (NetworkTraffic)
        END
        TESTCASE T002 BEGIN
            //USES S001 WITH NoNetworkTraffic // Error
            USES S002 WITH NoFileAccess
            NEEDS (NetworkTraffic)
        END
    ''')

    with (raises(textx.exceptions.TextXSemanticError)):
        meta_model.model_from_str('''
            ASPECT NetworkTraffic
            ASPECT FileAccess
            SCENARIO S001 BEGIN
                CONFIG HeavyNetworkTraffic HAS (NetworkTraffic)
                CONFIG NoNetworkTraffic HAS ()
            END
            SCENARIO S002 BEGIN
                CONFIG WithFileAccess HAS (NetworkTraffic FileAccess)
                CONFIG NoFileAccess HAS (NetworkTraffic)
            END
            TESTCASE T001 BEGIN
                USES S001 WITH HeavyNetworkTraffic
                NEEDS (NetworkTraffic)
            END
            TESTCASE T002 BEGIN
                USES S001 WITH NoNetworkTraffic // Error
                NEEDS (NetworkTraffic)
            END
        ''')
