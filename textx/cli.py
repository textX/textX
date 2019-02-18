#!/usr/bin/env python
import sys
import click
import pkg_resources
from textx import metamodel_from_file, TextXError
from textx.export import metamodel_export, model_export, PlantUmlRenderer


@click.group()
@click.option('--debug', default=False, is_flag=True,
              help="Debug/trace output.")
@click.pass_context
def textx(ctx, debug):
    ctx.obj = {'debug': debug}


meta_model_arg = click.argument('meta_model_file', type=click.Path())
model_arg = click.argument('model_file', type=click.Path(), required=False)
ignore_case_arg = click.option('--ignore-case/', '-i/', default=False,
                               is_flag=True,
                               help="case-insensitive parsing.")
format_arg = click.option('--output-format', '-f',
                          type=click.Choice(['dot', 'plantuml']),
                          default='dot',
                          help="select the output format (plantuml not "
                               "available for model files, yet.")


@textx.command()
@meta_model_arg
@model_arg
@ignore_case_arg
@click.pass_context
def check(ctx, meta_model_file, model_file, ignore_case):
    """
    Check validity of meta-model and optionally model.
    """
    debug = ctx.obj['debug']
    check_model(meta_model_file, model_file, debug, ignore_case)


@textx.command()
@meta_model_arg
@model_arg
@ignore_case_arg
@format_arg
@click.pass_context
def visualize(ctx, meta_model_file, model_file, ignore_case, output_format):
    """
    Generate .dot file(s) from meta-model and optionally model.
    """
    debug = ctx.obj['debug']
    meta_model, model = check_model(meta_model_file,
                                    model_file, debug, ignore_case)
    if output_format == 'plantuml':
        pu_file = "{}.pu".format(meta_model_file)
        click.echo("Generating '{}' file for meta-model.".format(pu_file))
        click.echo("To convert to png run 'plantuml {}'".format(pu_file))
        click.echo("To convert to svg run 'plantuml -tsvg {}'".format(pu_file))
        metamodel_export(meta_model, pu_file, PlantUmlRenderer())
    else:
        dot_file = "{}.dot".format(meta_model_file)
        click.echo("Generating '{}' file for meta-model.".format(dot_file))
        click.echo("To convert to png run 'dot -Tpng -O {}'".format(dot_file))
        metamodel_export(meta_model, dot_file)

    if model_file:
        if output_format == 'plantuml':
            raise Exception("plantuml is not supported for model files, yet.")
        dot_file = "{}.dot".format(model_file)
        click.echo("Generating '{}' file for model.".format(model_file))
        click.echo(
            "To convert to png run 'dot -Tpng -O {}'".format(model_file))
        model_export(model, dot_file)


def check_model(metamodel_file, model_file=None, debug=False,
                ignore_case=False):
    try:
        metamodel = metamodel_from_file(metamodel_file,
                                        ignore_case=ignore_case,
                                        debug=debug)
        click.echo("Meta-model OK.")
    except TextXError as e:
        click.echo("Error in meta-model file.")
        click.echo(e)
        sys.exit(1)

    model = None
    if model_file:
        try:
            model = metamodel.model_from_file(model_file, debug=debug)
            click.echo("Model OK.")
        except TextXError as e:
            click.echo("Error in model file.")
            click.echo(e)
            sys.exit(1)

    return metamodel, model


def register_textx_subcommands():
    """
    Find and use all textx sub-commands registered through extension points.
    Extension points for CLI extension are:
    - `textx_commands` - for registering top-level commands.
    - `textx_command_groups` - for registering command groups.
    """
    # Register direct sub-commands
    global textx
    for subcommand in pkg_resources.iter_entry_points(group='textx_commands'):
        textx.command()(subcommand.load())

    # Register sub-command groups
    for subgroup in pkg_resources.iter_entry_points(
            group='textx_command_groups'):
        subgroup.load()(textx)


# Register sub-commands registered through extension points.
register_textx_subcommands()
