from __future__ import unicode_literals
import sys
import os
import click
from textx import (metamodel_from_file,
                   metamodel_for_language,
                   metamodel_for_file)
from textx.exceptions import TextXError, TextXRegistrationError


@click.argument('model_files', type=click.Path(), required=False, nargs=-1)
@click.option('--language', help='A name of the language model conforms to.')
@click.option('--grammar',
              help='A file name of the grammar used as a meta-model.')
@click.option('--ignore-case/', '-i/', default=False,
              is_flag=True, help='Case-insensitive model parsing. '
              'Used only if "grammar" is provided.')
@click.pass_context
def check(ctx, model_files, language=None, grammar=None, ignore_case=False):
    """
    Validate model given its file path. If grammar is given use it to construct
    the meta-model. If language is given use it to retrieve the registered
    meta-model.

    Examples:

        # textX language is built-in, so always registered:

        textx check entity.tx

        # If the language is not registered you must provide the grammar:

        textx check person.ent --grammar entity.tx

        # or if we have language registered (see: text list-languages)
          it's just:

        textx check person.ent

        # Use "--language" if meta-model can't be deduced by file extension:

        textx check person.txt --language entity

        # Or to check multiple model files and deduce meta-model by extension

        textx check *

    """

    if not model_files:
        click.echo(ctx.get_help())
        sys.exit(1)

    debug = ctx.obj['debug']

    for model_file in model_files:
        try:
            if grammar:
                metamodel = metamodel_from_file(grammar, debug=debug,
                                                ignore_case=ignore_case)
            elif language:
                metamodel = metamodel_for_language(language)
            else:
                metamodel = metamodel_for_file(model_file)

            metamodel.model_from_file(model_file, debug=debug)
            click.echo("{}: OK.".format(os.path.abspath(model_file)))

        except TextXRegistrationError as e:
            click.echo(e.message)

        except TextXError as e:
            click.echo(e)
