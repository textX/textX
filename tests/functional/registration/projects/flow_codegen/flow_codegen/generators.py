import os

import click

from textx import GeneratorDesc


def codegen_flow_pu(metamodel, model, output_path, overwrite, debug=False, **custom_args):
    """
    This command transforms *.flow-files to *.pu files (plantuml).
    """

    txt = "@startuml\n"
    for a in model.algos:
        txt += f"component {a.name}\n"
    for f in model.flows:
        txt += f'{f.algo1.name} "{f.algo1.outp.name}" #--# {f.algo2.name}\n'
    txt += "@enduml\n"

    # Dump custom args for testing
    txt += "\n".join(
        [f"{arg_name}={arg_value}" for arg_name, arg_value in custom_args.items()]
    )

    input_file = model._tx_filename
    base_dir = output_path if output_path else os.path.dirname(input_file)
    base_name, _ = os.path.splitext(os.path.basename(input_file))
    output_file = os.path.abspath(os.path.join(base_dir, "{}.{}".format(base_name, "pu")))
    if overwrite or not os.path.exists(output_file):
        click.echo(f"-> {output_file}")
        with open(output_file, "w") as f:
            f.write(txt)
    else:
        click.echo(f"-- Skipping: {output_file}")


flow_pu = GeneratorDesc(
    language="flow-dsl",
    target="PlantUML",
    description="Generating PlantUML visualization from flow-dsl",
    generator=codegen_flow_pu,
)
