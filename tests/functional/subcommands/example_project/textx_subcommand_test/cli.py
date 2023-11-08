import click


def testcommand(textx):
    @textx.command()
    @click.argument("some_argument", type=click.Path())
    @click.option(
        "--some-option",
        default=False,
        is_flag=True,
        help="Testing option in custom command.",
    )
    def testcommand(some_argument, some_option):
        """
        This command will be found as a sub-command of `textx` command once
        this project is installed.
        """
        click.echo("Hello sub-command test!")


def create_testgroup(textx):
    @textx.group()
    @click.option(
        "--group-option", default=False, is_flag=True, help="Some group option."
    )
    def testgroup(group_option):
        """Here we write group explanation."""
        pass

    @testgroup.command()
    @click.argument("some_argument", type=click.Path())
    @click.option(
        "--some-option",
        default=False,
        is_flag=True,
        help="Testing option in custom command.",
    )
    def groupcommand1(some_argument, some_option):
        """And here we write a doc for particular command."""
        click.echo(f"GroupCommand1: argument: {some_argument}, option:{some_option}")

    @testgroup.command()
    def groupcommand2(some_argument, some_option):
        """This is another command docs."""
        click.echo(f"GroupCommand2: argument: {some_argument}, option:{some_option}")
