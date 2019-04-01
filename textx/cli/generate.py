import sys
import os
import click
from textx import (metamodel_for_file,
                   metamodel_for_language,
                   language_for_file,
                   generator_for_language_target,
                   TextXRegistrationError)


@click.argument('model_files', type=click.Path(), required=True, nargs=-1)
@click.option('--output-path', '-o', type=click.Path(), default=None,
              help='The output to generate to. Default = same as input.')
@click.option('--language',
              help='A name of the language model conforms to.'
              ' Deduced from file name if not given.')
@click.option('--target', help='Target output format.', required=True)
@click.option('--overwrite', is_flag=True, default=False, required=False,
              help='Should overwrite output files if exist.')
@click.pass_context
def generate(ctx, model_files, output_path, language, target, overwrite):
    """
    Run code generator on a provided model(s).

    For example::

    \b
    # Generate PlantUML output from .flow models
    textx generate mymodel.flow --target PlantUML

    \b
    # or with defined output folder
    textx generate mymodel.flow rendered_model/ --target PlantUML

    \b
    # To chose language by name and not by file pattern use --language
    textx generate *.flow --language flow --target PlantUML

    \b
    # Use --overwrite to overwrite target files
    textx generate mymodel.flow --target PlantUML --overwrite

    \b
    # In all above cases PlantUML generator must be registered:
    $ textx list-generators
    flow-dsl -> PlantUML  Generating PlantUML visualization from flow-dsl
    """

    if not model_files:
        click.echo(ctx.get_help())
        sys.exit(1)

    click.echo('Generating {} target from models:'.format(target))

    for model_file in model_files:
        click.echo(os.path.abspath(model_file))
        if language:
            metamodel = metamodel_for_language(language)
        else:
            language = language_for_file(model_file).name
            metamodel = metamodel_for_file(model_file)

        model = metamodel.model_from_file(model_file)

        try:
            generator = generator_for_language_target(language, target)
        except TextXRegistrationError as e:
            click.echo(e.message)
            sys.exit(1)

        generator(model, output_path, overwrite)
