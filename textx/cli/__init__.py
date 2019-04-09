import click
import pkg_resources


@click.group()
@click.option('--debug', default=False, is_flag=True,
              help="Debug/trace output.")
@click.pass_context
def textx(ctx, debug):
    ctx.obj = {'debug': debug}


def register_textx_subcommands():
    """
    Find and use all textx sub-commands registered through extension points.
    Extension points for CLI extension are:
    - `textx_commands` - for registering top-level commands.
    - `textx_command_groups` - for registering command groups.
    """
    # Register direct sub-commands
    global textx
    for subcommand in pkg_resources.iter_entry_points(group='textx_commands'):
        textx.command()(subcommand.load())

    # Register sub-command groups
    for subgroup in pkg_resources.iter_entry_points(
            group='textx_command_groups'):
        subgroup.load()(textx)


# Register sub-commands registered through extension points.
register_textx_subcommands()
