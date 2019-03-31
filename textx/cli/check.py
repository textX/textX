from __future__ import unicode_literals
import sys
import click
from textx import (metamodel_from_file,
                   metamodel_for_language,
                   metamodel_for_file)
from textx.exceptions import TextXError, TextXRegistrationError


@click.argument('model_file', type=click.Path(), required=False)
@click.option('--language', help='A name of the language model conforms to.')
@click.option('--grammar',
              help='A file name of the grammar used as a meta-model.')
@click.option('--ignore-case/', '-i/', default=False,
              is_flag=True, help='Case-insensitive model parsing. '
              'Used only if "grammar" is provided.')
@click.pass_context
def check(ctx, model_file, language=None, grammar=None, ignore_case=False):
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

    """

    if not model_file:
        click.echo(ctx.get_help())
        sys.exit(1)

    debug = ctx.obj['debug']

    try:
        if grammar:
            metamodel = metamodel_from_file(grammar, debug=debug,
                                            ignore_case=ignore_case)
        elif language:
            metamodel = metamodel_for_language(language)
        else:
            metamodel = metamodel_for_file(model_file)
    except TextXRegistrationError as e:
        click.echo(e.message)
        sys.exit(1)

    try:
        metamodel.model_from_file(model_file, debug=debug)
        click.echo("(Meta-)model OK.")
    except TextXError as e:
        click.echo("Error in (meta-)model file.")
        click.echo(e)
        sys.exit(1)
