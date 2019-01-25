#!/usr/bin/env python
from __future__ import unicode_literals
import sys
import click
from textx import metamodel_from_file, TextXError
from textx.export import metamodel_export, model_export


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
@click.pass_context
def visualize(ctx, meta_model_file, model_file, ignore_case):
    """
    Generate .dot file(s) from meta-model and optionally model.
    """
    debug = ctx.obj['debug']
    meta_model, model = check_model(meta_model_file,
                                    model_file, debug, ignore_case)
    dot_file = "{}.dot".format(meta_model_file)
    click.echo("Generating '{}' file for meta-model.".format(dot_file))
    click.echo("To convert to png run 'dot -Tpng -O {}'".format(dot_file))
    metamodel_export(meta_model, dot_file)

    if model_file:
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


if __name__ == '__main__':
    textx()
