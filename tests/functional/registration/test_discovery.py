"""
Test discovering of registered languages and generators.
"""
from click.testing import CliRunner

from textx.cli import textx


def test_list_languages_cli(caplog):
    """
    Test list-languages command.
    """
    runner = CliRunner()
    result = runner.invoke(textx, ["list-languages"])
    assert result.exit_code == 0
    assert "flow-dsl[1.0.0]" in caplog.text
    assert "*.eflow" in caplog.text
    assert "data-dsl" in caplog.text


def test_list_generators_cli(caplog):
    """
    Test list-generators command.
    """
    runner = CliRunner()
    result = runner.invoke(textx, ["list-generators"])
    assert result.exit_code == 0
    assert "flow-dsl -> PlantUML" in caplog.text
    assert "flow-codegen[1.0.0]" in caplog.text
