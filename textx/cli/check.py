try:
    import click
except ImportError as e:
    raise Exception(
        "textX must be installed with CLI dependencies to use "
        "textx command.\npip install textX[cli]"
    ) from e
import os

from textx import (
    TextXError,
    TextXRegistrationError,
    metamodel_for_file,
    metamodel_for_language,
    metamodel_from_file,
)


def check(textx):
    @textx.command()
    @click.argument("model_files", type=click.Path(), required=True, nargs=-1)
    @click.option("--language", help="A name of the language model conforms to.")
    @click.option("--grammar", help="A file name of the grammar used as a meta-model.")
    @click.option(
        "--ignore-case/",
        "-i/",
        default=False,
        is_flag=True,
        help="Case-insensitive model parsing. " 'Used only if "grammar" is provided.',
    )
    @click.pass_context
    def check(ctx, model_files, language=None, grammar=None, ignore_case=False):
        """
        Check/validate model given its file path. If grammar is given use it to
        construct the meta-model. If language is given use it to retrieve the
        registered meta-model.

        Examples:

        \b
        # textX language is built-in, so always registered:
        textx check entity.tx

        \b
        # If the language is not registered you must provide the grammar:
        textx check person.ent --grammar entity.tx

        \b
        # or if we have language registered (see: text list-languages) it's just:
        textx check person.ent

        \b
        # Use "--language" if meta-model can't be deduced by file extension:
        textx check person.txt --language entity

        \b
        # Or to check multiple model files and deduce meta-model by extension
        textx check *

        """  # noqa

        debug = ctx.obj["debug"]

        try:
            per_file_metamodel = False
            if grammar:
                metamodel = metamodel_from_file(
                    grammar, debug=debug, ignore_case=ignore_case
                )
            elif language:
                metamodel = metamodel_for_language(language)
            else:
                per_file_metamodel = True

            for model_file in model_files:
                if per_file_metamodel:
                    metamodel = metamodel_for_file(model_file)

                metamodel.model_from_file(model_file, debug=debug)
                click.echo(f"{os.path.abspath(model_file)}: OK.")

        except TextXRegistrationError as e:
            raise click.ClickException(e.message) from e

        except TextXError as e:
            raise click.ClickException(str(e)) from e
