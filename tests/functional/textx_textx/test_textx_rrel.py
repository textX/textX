from os.path import abspath, dirname, join

from textx import get_children_of_type, metamodel_for_language


def test_textx_rrel_multi():
    textx_mm = metamodel_for_language("textx")
    grammar_model = textx_mm.grammar_model_from_file(
        join(abspath(dirname(__file__)), "textx_rrel_test.tx")
    )

    rrels = get_children_of_type("RRELExpression", grammar_model)

    # Multi
    assert rrels[0].multi

    # Multi with parent
    assert (
        rrels[1].multi
        and rrels[1].sequence.paths[0].parts[0].__class__.__name__ == "RRELParent"
    )

    # Dots
    dots = get_children_of_type("RRELPath", rrels[3])
    assert any([x.dots == ".." for x in dots])

    # Brackets
    brackets = get_children_of_type("RRELBrackets", rrels[4])
    assert len(brackets) == 1


def test_obj_ref_rule_without_rrel():
    textx_mm = metamodel_for_language("textx")
    grammar_model = textx_mm.grammar_model_from_str(
        "Model: ref=[Target:FQN]; FQN: ID+['.'];"
    )

    obj_refs = get_children_of_type("ObjRef", grammar_model)

    assert len(obj_refs) == 1
    assert obj_refs[0].name == "Target"
    assert obj_refs[0].obj_ref_rule == "FQN"
    assert obj_refs[0].rrel is None


def test_obj_ref_rule_with_rrel():
    textx_mm = metamodel_for_language("textx")
    grammar_model = textx_mm.grammar_model_from_str(
        "Model: ref=[Target:FQN|+m:items*]; FQN: ID+['.'];"
    )

    obj_refs = get_children_of_type("ObjRef", grammar_model)

    assert len(obj_refs) == 1
    assert obj_refs[0].obj_ref_rule == "FQN"
    assert obj_refs[0].rrel is not None
    assert obj_refs[0].rrel.multi
