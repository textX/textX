"""
Test discovering of registered languages and generators.
"""
from click.testing import CliRunner

from textx.cli import textx


def test_list_languages_cli():
    """
    Test list-languages command.
    """
    runner = CliRunner()
    result = runner.invoke(textx, ["list-languages"])
    assert result.exit_code == 0
    assert "flow-dsl[1.0.0]" in result.output
    assert "*.eflow" in result.output
    assert "data-dsl" in result.output


def test_list_generators_cli():
    """
    Test list-generators command.
    """
    runner = CliRunner()
    result = runner.invoke(textx, ["list-generators"])
    assert result.exit_code == 0
    assert "flow-dsl -> PlantUML" in result.output
    assert "flow-codegen[1.0.0]" in result.output
