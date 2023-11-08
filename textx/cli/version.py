try:
    import click
except ImportError:
    raise Exception(
        "textX must be installed with CLI dependencies to use "
        "textx command.\npip install textX[cli]"
    )


def version(textx):
    @textx.command()
    def version():
        """
        Print version info.
        """
        import textx

        click.echo(f"textX {textx.__version__}")
