import logging

from textx.registration import generator_descriptions, language_descriptions

logger = logging.getLogger(__name__)


def list_languages(textx):
    @textx.command()
    def list_languages():
        """
        List all registered languages
        """
        for language in language_descriptions().values():
            logger.info(
                "{:<30}{:<40}{}".format(
                    f"{language.name} ({language.pattern})",
                    f"{language.project_name}[{language.project_version}]",
                    language.description,
                )
            )


def list_generators(textx):
    @textx.command()
    def list_generators():
        """
        List all registered generators
        """
        for language in generator_descriptions().values():
            for generator in language.values():
                logger.info(
                    "{:<30}{:<30}{}".format(
                        f"{generator.language} -> {generator.target}",
                        f"{generator.project_name}[{generator.project_version}]",
                        generator.description,
                    )
                )
