try:
    import click
except ImportError:
    raise Exception('textX must be installed with CLI dependencies to use '
                    'textx command.\npip install textX[cli]')

from textx.registration import (language_descriptions,
                                generator_descriptions)


def list_languages(textx):
    @textx.command()
    def list_languages():
        """
        List all registered languages
        """
        for language in language_descriptions().values():
            click.echo("{:<30}{:<40}{}"
                       .format("{} ({})".format(language.name,
                                                language.pattern),
                               "{}[{}]".format(language.project_name,
                                               language.project_version),
                               language.description))


def list_generators(textx):
    @textx.command()
    def list_generators():
        """
        List all registered generators
        """
        for language in generator_descriptions().values():
            for generator in language.values():
                click.echo("{:<30}{:<30}{}"
                           .format("{} -> {}".format(generator.language,
                                                     generator.target),
                                   "{}[{}]".format(generator.project_name,
                                                   generator.project_version),
                                   generator.description))
