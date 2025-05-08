import logging

logger = logging.getLogger(__name__)


def version(textx):
    @textx.command()
    def version():
        """
        Print version info.
        """
        import textx

        logger.info("textX %s", textx.__version__)
