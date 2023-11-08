"""
Test `version` command.
"""
from click.testing import CliRunner
from packaging.version import parse

from textx.cli import textx


def test_version_command():
    runner = CliRunner()
    result = runner.invoke(textx, ["version"])
    assert result.exit_code == 0
    assert result.output.startswith("textX")
    version_text = result.output.split()[-1]
    version = parse(version_text)
    assert version.__class__.__name__ == "Version"
