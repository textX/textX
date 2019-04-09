import sys
import os
import click
from textx import (metamodel_from_file,
                   metamodel_for_file,
                   metamodel_for_language,
                   language_for_file,
                   generator_for_language_target,
                   TextXRegistrationError, TextXError)


@click.argument('model_files', type=click.Path(), required=True, nargs=-1)
@click.option('--output-path', '-o', type=click.Path(), default=None,
              help='The output to generate to. Default = same as input.')
@click.option('--language',
              help='A name of the language model conforms to.'
              ' Deduced from file name if not given.')
@click.option('--target', help='Target output format.', required=True)
@click.option('--overwrite', is_flag=True, default=False, required=False,
              help='Should overwrite output files if exist.')
@click.option('--grammar',
              help='A file name of the grammar used as a meta-model.')
@click.option('--ignore-case/', '-i/', default=False, is_flag=True,
              help='Case-insensitive model parsing. '
              'Used only if "grammar" is provided.')
@click.pass_context
def generate(ctx, model_files, output_path, language, target, overwrite,
             grammar=None, ignore_case=False):
    """
    Run code generator on a provided model(s).

    For example::

    \b
    # Generate PlantUML output from .flow models
    textx generate mymodel.flow --target PlantUML

    \b
    # or with defined output folder
    textx generate mymodel.flow -o rendered_model/ --target PlantUML

    \b
    # To chose language by name and not by file pattern use --language
    textx generate *.flow --language flow --target PlantUML

    \b
    # Use --overwrite to overwrite target files
    textx generate mymodel.flow --target PlantUML --overwrite

    \b
    # If the language is not registered you can use the .tx grammar file
    textx generate --grammar Flow.tx --target PlantUML mymodel.flow

    \b
    # In all above cases PlantUML generator must be registered:
    $ textx list-generators
    flow-dsl -> PlantUML  Generating PlantUML visualization from flow-dsl

    """

    debug = ctx.obj['debug']
    click.echo('Generating {} target from models:'.format(target))

    try:
        per_file_metamodel = False
        if grammar:
            metamodel = metamodel_from_file(grammar, debug=debug,
                                            ignore_case=ignore_case)
        elif language:
            metamodel = metamodel_for_language(language)
        else:
            per_file_metamodel = True

        for model_file in model_files:
            click.echo(os.path.abspath(model_file))

            if per_file_metamodel:
                language = language_for_file(model_file).name
                metamodel = metamodel_for_file(model_file)
            model = metamodel.model_from_file(model_file)
            generator = generator_for_language_target(
                language, target, any_permitted=per_file_metamodel)

            generator(metamodel, model, output_path, overwrite, debug)

    except TextXRegistrationError as e:
        click.echo(e.message)

    except TextXError as e:
        click.echo(e)
