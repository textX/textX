import textx


def test_issue166_wrong_multiple_rule_reference():
    """
    Test wrongly detected referencing of multiple rules from a single abstract
    rule alternative.
    Reported in issue #166.
    """
    grammar = """
    DSL:
        commands*=BaseCommand;
    BaseCommand:
        (Require | Group) '.'?;

    Require:
        'require' /[a-z]/;
    Group:
        'group' hello=/[0-9]/;
    """

    metamodel = textx.metamodel_from_str(grammar)
    assert metamodel
    model = metamodel.model_from_str("require a. group 4")
    assert model.commands[0] == "requirea"
    assert model.commands[1].hello == "4"
