import click
import os
from textx import GeneratorDesc
from textx.export import metamodel_export, model_export, PlantUmlRenderer


def metamodel_generate_dot(metamodel, model, output_path, overwrite, debug):
    """
    This generator transforms *.tx file to a *.dot file (GraphViz dot).
    """
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


def model_generate_dot(metamodel, model, output_path, overwrite, debug):
    """
    This generator transforms arbitrary textX model to *.dot file
    (GraphViz dot).
    """
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


def metamodel_generate_plantuml(metamodel, model, output_path, overwrite,
                                debug):
    """
    This generator transforms *.tx file to a *.pu file (PlantUML).
    """
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


metamodel_gen_dot = GeneratorDesc(
    language='textX',
    target='dot',
    description='Generating dot visualizations from textX grammars',
    generator=metamodel_generate_dot)


model_gen_dot = GeneratorDesc(
    language='any',
    target='dot',
    description='Generating dot visualizations from arbitrary models',
    generator=model_generate_dot)


metamodel_gen_plantuml = GeneratorDesc(
    language='textX',
    target='PlantUML',
    description='Generating PlantUML visualizations from textX grammars',
    generator=metamodel_generate_plantuml)
