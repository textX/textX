import click
import os
from textx import GeneratorDesc


def codegen_flow_pu(metamodel, model, output_path, overwrite, debug=False,
                    **custom_args):
    """
    This command transforms *.flow-files to *.pu files (plantuml).
    """

    txt = "@startuml\n"
    for a in model.algos:
        txt += "component {}\n".format(a.name)
    for f in model.flows:
        txt += '{} "{}" #--# {}\n'.format(f.algo1.name, f.algo1.outp.name,
                                          f.algo2.name)
    txt += "@enduml\n"

    # Dump custom args for testing
    txt += '\n'.join(["{}={}".format(arg_name, arg_value)
                      for arg_name, arg_value in custom_args.items()])

    input_file = model._tx_filename
    base_dir = output_path if output_path else os.path.dirname(input_file)
    base_name, _ = os.path.splitext(os.path.basename(input_file))
    output_file = os.path.abspath(
        os.path.join(base_dir, "{}.{}".format(base_name, 'pu')))
    if overwrite or not os.path.exists(output_file):
        click.echo('-> {}'.format(output_file))
        with open(output_file, "w") as f:
            f.write(txt)
    else:
        click.echo('-- Skipping: {}'.format(output_file))


flow_pu = GeneratorDesc(
    language='flow-dsl',
    target='PlantUML',
    description='Generating PlantUML visualization from flow-dsl',
    generator=codegen_flow_pu)
