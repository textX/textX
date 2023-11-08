import subprocess


def test_subcommand():
    """
    Test that a command from the example project is registered.
    """
    output = subprocess.check_output(["textx"], stderr=subprocess.STDOUT)
    assert b"testcommand" in output


def test_subcommand_group():
    """
    Test that a command group is registered.
    """
    output = subprocess.check_output(["textx", "testgroup"], stderr=subprocess.STDOUT)
    assert b"groupcommand1" in output
    assert b"groupcommand2" in output
