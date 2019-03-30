import click

from textx.registration import (get_language_descriptions,
                                get_generator_descriptions)


def list_languages():
    """
    List all registered languages
    """
    for language in get_language_descriptions().values():
        click.echo("{}({})\t\t{}".format(language.name,
                                         language.extension,
                                         language.description))


def list_generators():
    """
    List all registered generators
    """
    generators = get_generator_descriptions()
    for language in generators.values():
        for generator in language.values():
            click.echo("{}->{}\t\t{}".format(generator.language,
                                             generator.target,
                                             generator.desciption))
