import subprocess


def test_subcommand():
    """
    Test that a command from the example project is registered.
    """
    result = subprocess.run(["textx"], capture_output=True, check=False)
    assert b"testcommand" in (result.stdout + result.stderr)


def test_subcommand_group():
    """
    Test that a command group is registered.
    """
    result = subprocess.run(["textx", "testgroup"],
                            capture_output=True, check=False)
    assert b"groupcommand1" in (result.stdout + result.stderr)
    assert b"groupcommand2" in (result.stdout + result.stderr)
