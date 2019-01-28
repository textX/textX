import os
import pytest
import subprocess


@pytest.fixture(scope="session")
def example_project():
    this_folder = os.path.dirname(__file__)
    output = subprocess.check_output(
        ['pip', 'install', '-e', os.path.join(this_folder, 'example_project')],
        stderr=subprocess.STDOUT)
    assert b'Successfully installed textX-subcommand-test' in output


def test_single_subcommand(example_project):
    """
    Test that a single top-level command from the example project is
    registered.
    """
    output = subprocess.check_output(['textx'], stderr=subprocess.STDOUT)
    assert b'testcommand' in output


def test_subcommand_group(example_project):
    """
    Test that a command group is registered.
    """
    output = subprocess.check_output(['textx', 'testgroup'],
                                     stderr=subprocess.STDOUT)
    assert b'groupcommand1' in output
    assert b'groupcommand2' in output
