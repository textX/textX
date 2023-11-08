try:
    import click
except ImportError as e:
    raise Exception(
        "textX must be installed with CLI dependencies to use "
        "textx command.\npip install textX[cli]"
    ) from e

import sys

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points


@click.group()
@click.option("--debug", default=False, is_flag=True, help="Debug/trace output.")
@click.pass_context
def textx(ctx, debug):
    ctx.obj = {"debug": debug}


def register_textx_subcommands():
    """
    Find and use all textx sub-commands registered through the extension point.

    Entry point used for commands registration is `textx_commands`.
    In this entry point you should register a callable that accepts the top
    level click `textx` command and register additional commands(s) on it.
    """
    global textx
    for subcommand in entry_points(group="textx_commands"):
        subcommand.load()(textx)


# Register sub-commands specified through extension points.
register_textx_subcommands()
