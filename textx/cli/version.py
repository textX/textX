from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import click

logger = logging.getLogger(__name__)


def version(textx: click.Group) -> None:
    @textx.command()
    def version() -> None:
        """
        Print version info.
        """
        import textx

        logger.info("textX %s", textx.__version__)
