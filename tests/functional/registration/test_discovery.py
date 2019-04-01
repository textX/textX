"""
Test discovering of registered languages and generators.
"""
import subprocess


def test_list_languages_cli():
    """
    Test list-languages command.
    """
    output = subprocess.check_output(['textx', 'list-languages'],
                                     stderr=subprocess.STDOUT)
    assert b'flow-dsl' in output
    assert b'*.eflow' in output
    assert b'data-dsl' in output


def test_list_generators_cli():
    """
    Test list-generators command.
    """
    output = subprocess.check_output(['textx', 'list-generators'],
                                     stderr=subprocess.STDOUT)
    assert b'flow-dsl -> PlantUML' in output
