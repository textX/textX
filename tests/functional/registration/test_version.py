"""
Test `version` command.
"""
from click.testing import CliRunner
from packaging.version import parse

from textx.cli import textx


def test_version_command(caplog):
    runner = CliRunner()
    result = runner.invoke(textx, ["version"])
    assert result.exit_code == 0
    assert 'textX' in caplog.text
    version_text = caplog.text.split()[-1]
    version = parse(version_text)
    assert version.__class__.__name__ == "Version"
