"""
Test `version` command.
"""
from pkg_resources import parse_version
from textx.cli import textx
from click.testing import CliRunner


def test_version_command():
    runner = CliRunner()
    result = runner.invoke(textx, ['version'])
    assert result.exit_code == 0
    assert result.output.startswith('textX')
    version_text = result.output.split()[-1]
    version = parse_version(version_text)
    assert version.__class__.__name__ == 'Version'
