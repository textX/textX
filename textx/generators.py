import os
from functools import partial

from textx.export import PlantUmlRenderer, metamodel_export, model_export
from textx.registration import generator


def get_output_filename(input_file, output_path, fileext):
    """
    Helper function used to create output file based on output path, input_file
    base name and extension.
    Args:
        fileext (str): Target file name extension.
        input_file (str): Input file name
        output_path (str): Output folder
    """

    base_dir = output_path if output_path else os.path.dirname(input_file)
    base_name, _ = os.path.splitext(os.path.basename(input_file))
    output_file = os.path.abspath(os.path.join(base_dir, f"{base_name}.{fileext}"))
    return output_file


def gen_file(
    input_file, output_file, gen_callback, overwrite=False, success_message="Done."
):
    """
    A helper function to implement common logic for generating of a single
    file. Handling of output name creation, skipping existing files, handling
    overwrite flag.

    Args:
        input_file (str): Input file name
        output_file (str): Output file name
        gen_callback(callable): Generator callback
        overwrite (bool): Should overwrite target file if exists
        success_message (str): A message displayed to user after generation is
            complete.
    """
    try:
        import click
    except ImportError as e:
        raise Exception(
            "textX must be installed with CLI dependencies to use "
            "textx command.\npip install textX[cli]"
        ) from e
    if overwrite or not os.path.exists(output_file):
        click.echo(f"-> {output_file}")
        gen_callback()
        click.echo("    " + success_message)
    else:
        click.echo(click.style("-- NOT overwriting: ", fg="red", bold=True), nl=False)
        click.echo(output_file)


@generator("textX", "dot")
def metamodel_generate_dot(metamodel, model, output_path, overwrite, debug):
    "Generating dot visualizations from textX grammars"

    output_file = get_output_filename(model.file_name, output_path, "dot")
    gen_file(
        model.file_name,
        output_file,
        partial(metamodel_export, model, output_file),
        overwrite,
        success_message=f'To convert to png run '
                        f'"dot -Tpng -O {os.path.basename(output_file)}"',
    )


@generator("any", "dot")
def model_generate_dot(metamodel, model, output_path, overwrite, debug):
    "Generating dot visualizations from arbitrary models"

    output_file = get_output_filename(model._tx_filename, output_path, "dot")
    gen_file(
        model._tx_filename,
        output_file,
        partial(model_export, model, output_file),
        overwrite,
        success_message=f'To convert to png run '
                        f'"dot -Tpng -O {os.path.basename(output_file)}"',
    )


@generator("textX", "PlantUML")
def metamodel_generate_plantuml(metamodel, model, output_path, overwrite,
                                debug, **custom_args):
    "Generating PlantUML visualizations from textX grammars"

    output_file = get_output_filename(model.file_name, output_path, "pu")
    linetype = custom_args.get('linetype')

    gen_file(
        model.file_name,
        output_file,
        partial(metamodel_export, model, output_file,
                renderer=PlantUmlRenderer(linetype)),
        overwrite,
        success_message=f'To convert to png run '
                        f'"plantuml {os.path.basename(output_file)}"',
    )
