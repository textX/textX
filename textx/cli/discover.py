import click

from textx.registration import (language_descriptions,
                                generator_descriptions)


def list_languages():
    """
    List all registered languages
    """
    for language in language_descriptions().values():
        click.echo("{}({})\t\t{}".format(language.name,
                                         language.extension,
                                         language.description))


def list_generators():
    """
    List all registered generators
    """
    for language in generator_descriptions().values():
        for generator in language.values():
            click.echo("{}->{}\t\t{}".format(generator.language,
                                             generator.target,
                                             generator.desciption))
