import io

from textx import metamodel_from_str
from textx.export import model_export_to_file


def test_export_empty_match_rule_model():
    """Match-rule roots may be empty strings; export must not treat them as omitted."""
    mm = metamodel_from_str('Model: "hello"?;')
    model = mm.model_from_str("")
    assert model == ""

    out = io.StringIO()
    model_export_to_file(out, model)
    text = out.getvalue()
    assert "digraph textX" in text


def test_export_rejects_missing_model_and_repo():
    out = io.StringIO()
    try:
        model_export_to_file(out, None, None)
        assert False, "expected Exception"
    except Exception as err:
        assert "specify either a model or a repo" in str(err)
