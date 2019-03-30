import click
import pkg_resources

# Registered languages keyed by their names
languages = None
generators = None


def list_languages():
    """
    List all registered languages
    """
    global languages
    if languages is None:
        languages = {}
        for language in pkg_resources.iter_entry_points(
                group='textx_languages'):
            languages[language.name] = language.load()
    for language in languages.values():
        click.echo("{}({})\t\t{}".format(language.name,
                                         language.extension,
                                         language.description))


def list_generators():
    """
    List all registered generators
    """
    global generators
    if generators is None:
        generators = {}
        for generator in pkg_resources.iter_entry_points(
                group='textx_languages'):
            generator[generator.name] = generator.load()
    for generator in generators.values():
        click.echo("{}->{}\t\t{}".format(generator.language,
                                         generator.target,
                                         generator.desciption))
