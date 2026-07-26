from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import click

from textx.registration import generator_descriptions, language_descriptions

logger = logging.getLogger(__name__)


def list_languages(textx: click.Group) -> None:
    @textx.command()
    def list_languages() -> None:
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


def list_generators(textx: click.Group) -> None:
    @textx.command()
    def list_generators() -> None:
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
