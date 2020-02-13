import click


def version(textx):
    @textx.command()
    def version():
        """
        Print version info.
        """
        import textx
        click.echo('textX {}'.format(textx.__version__))
