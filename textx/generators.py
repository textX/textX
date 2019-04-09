import click
import os
from textx import generator
from textx.export import metamodel_export, model_export, PlantUmlRenderer


@generator('textX', 'dot')
def metamodel_generate_dot(metamodel, model, output_path, overwrite, debug):
    "Generating dot visualizations from textX grammars"

    input_file = model.file_name
    base_dir = output_path if output_path else os.path.dirname(input_file)
    base_name, _ = os.path.splitext(os.path.basename(input_file))
    output_file = os.path.abspath(
        os.path.join(base_dir, "{}.{}".format(base_name, 'dot')))
    if overwrite or not os.path.exists(output_file):
        click.echo('-> {}'.format(output_file))
        metamodel_export(model, output_file)
        click.echo('   To convert to png run "dot -Tpng -O {}"'
                   .format(os.path.basename(output_file)))
    else:
        click.echo('-- Skipping: {}'.format(output_file))


@generator('any', 'dot')
def model_generate_dot(metamodel, model, output_path, overwrite, debug):
    "Generating dot visualizations from arbitrary models"

    input_file = model._tx_filename
    base_dir = output_path if output_path else os.path.dirname(input_file)
    base_name, _ = os.path.splitext(os.path.basename(input_file))
    output_file = os.path.abspath(
        os.path.join(base_dir, "{}.{}".format(base_name, 'dot')))
    if overwrite or not os.path.exists(output_file):
        click.echo('-> {}'.format(output_file))
        model_export(model, output_file)
        click.echo('   To convert to png run "dot -Tpng -O {}"'
                   .format(os.path.basename(output_file)))
    else:
        click.echo('-- Skipping: {}'.format(output_file))


@generator('textX', 'PlantUML')
def metamodel_generate_plantuml(metamodel, model, output_path, overwrite,
                                debug):
    "Generating PlantUML visualizations from textX grammars"

    input_file = model.file_name
    base_dir = output_path if output_path else os.path.dirname(input_file)
    base_name, _ = os.path.splitext(os.path.basename(input_file))
    output_file = os.path.abspath(
        os.path.join(base_dir, "{}.{}".format(base_name, 'pu')))
    if overwrite or not os.path.exists(output_file):
        click.echo('-> {}'.format(output_file))
        metamodel_export(model, output_file, PlantUmlRenderer())
        click.echo("To convert to png run 'plantuml {}'".format(output_file))
    else:
        click.echo('-- Skipping: {}'.format(output_file))
