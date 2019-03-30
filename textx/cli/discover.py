import click
import pkg_resources


def list_languages():
    """
    List all registered languages
    """
    for language in pkg_resources.iter_entry_points(
            group='textx_languages'):
        language = language.load()
        click.echo("{}({})\t\t{}".format(language.name,
                                         language.extension,
                                         language.description))


def list_generators():
    """
    List all registered generators
    """
    for generator in pkg_resources.iter_entry_points(
            group='textx_generators'):
        generator = generator.load()
        click.echo("{}->{}\t\t{}".format(generator.language,
                                         generator.target,
                                         generator.desciption))
